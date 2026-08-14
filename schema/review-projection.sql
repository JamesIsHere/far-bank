PRAGMA foreign_keys = ON;

CREATE TABLE projection_manifest (
    manifest_id TEXT PRIMARY KEY,
    builder_id TEXT NOT NULL,
    builder_version TEXT NOT NULL,
    built_at TEXT NOT NULL,
    canonical_input_manifest_json TEXT NOT NULL
) STRICT;

CREATE TABLE question_identity (
    question_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    creation_provenance_json TEXT NOT NULL
) STRICT;

CREATE TABLE reference_version (
    reference_version_id TEXT PRIMARY KEY,
    reference_id TEXT NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    record_purpose TEXT NOT NULL,
    authority_class TEXT NOT NULL,
    record_json TEXT NOT NULL,
    UNIQUE (reference_id, version_number)
) STRICT;

CREATE TABLE rule_version (
    rule_version_id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    content_json TEXT NOT NULL,
    UNIQUE (rule_id, version_number)
) STRICT;

CREATE TABLE rule_source_reference (
    rule_version_id TEXT NOT NULL REFERENCES rule_version(rule_version_id),
    citation_ordinal INTEGER NOT NULL CHECK (citation_ordinal > 0),
    reference_version_id TEXT NOT NULL REFERENCES reference_version(reference_version_id),
    citation_role TEXT NOT NULL,
    PRIMARY KEY (rule_version_id, citation_ordinal)
) STRICT;

CREATE TABLE question_version (
    version_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL REFERENCES question_identity(question_id),
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    content_json TEXT NOT NULL,
    UNIQUE (question_id, version_number)
) STRICT;

CREATE TABLE question_option (
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    option_id TEXT NOT NULL CHECK (option_id IN ('A', 'B', 'C', 'D')),
    option_text TEXT NOT NULL,
    is_keyed INTEGER NOT NULL CHECK (is_keyed IN (0, 1)),
    error_model_json TEXT,
    PRIMARY KEY (version_id, option_id)
) STRICT;

CREATE UNIQUE INDEX one_keyed_option_per_version
ON question_option(version_id)
WHERE is_keyed = 1;

CREATE TABLE blueprint_mapping (
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    mapping_ordinal INTEGER NOT NULL CHECK (mapping_ordinal > 0),
    taxonomy_id TEXT NOT NULL,
    area_id TEXT NOT NULL,
    group_id TEXT NOT NULL,
    topic_id TEXT,
    representative_task_id TEXT NOT NULL,
    skill_level TEXT NOT NULL,
    mapping_rationale TEXT NOT NULL,
    mcq_scope_limit TEXT NOT NULL,
    PRIMARY KEY (version_id, mapping_ordinal)
) STRICT;

CREATE TABLE difficulty_dimension (
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    dimension_id TEXT NOT NULL,
    rubric_version_id TEXT NOT NULL,
    rubric_status TEXT NOT NULL CHECK (rubric_status = 'proposed_for_g2'),
    provisional_level INTEGER NOT NULL CHECK (provisional_level BETWEEN 1 AND 5),
    observable_measurements_json TEXT NOT NULL,
    PRIMARY KEY (version_id, dimension_id)
) STRICT;

CREATE TABLE question_rule_trace (
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    trace_ordinal INTEGER NOT NULL CHECK (trace_ordinal > 0),
    rule_version_id TEXT NOT NULL REFERENCES rule_version(rule_version_id),
    assertion_ids_json TEXT NOT NULL,
    PRIMARY KEY (version_id, trace_ordinal)
) STRICT;

CREATE TABLE required_check_policy (
    required_check_set_id TEXT PRIMARY KEY,
    required_pass_count INTEGER NOT NULL CHECK (required_pass_count > 0)
) STRICT;

CREATE TABLE required_check_policy_item (
    required_check_set_id TEXT NOT NULL REFERENCES required_check_policy(required_check_set_id),
    check_id TEXT NOT NULL,
    PRIMARY KEY (required_check_set_id, check_id)
) STRICT;

CREATE TABLE verification_event (
    event_id TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    question_id TEXT NOT NULL REFERENCES question_identity(question_id),
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    checker_id TEXT NOT NULL,
    checker_version TEXT NOT NULL,
    required_check_set_id TEXT NOT NULL,
    input_evidence_json TEXT NOT NULL
) STRICT;

CREATE TABLE verification_check (
    event_id TEXT NOT NULL REFERENCES verification_event(event_id),
    check_id TEXT NOT NULL,
    category TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('pass', 'fail', 'flag')),
    detail TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    calibration_fixture_ids_json TEXT NOT NULL,
    PRIMARY KEY (event_id, check_id)
) STRICT;

CREATE TABLE review_event (
    event_id TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('approve', 'reject', 'revise', 'comment', 'auto_invalidate')),
    actor_type TEXT NOT NULL CHECK (actor_type IN ('human', 'system')),
    actor_id TEXT NOT NULL,
    display_name TEXT NOT NULL,
    question_id TEXT NOT NULL REFERENCES question_identity(question_id),
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    comment TEXT NOT NULL,
    reason_code TEXT,
    superseding_version_id TEXT
) STRICT;

CREATE TABLE source_impact_event (
    event_id TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    actor_type TEXT NOT NULL CHECK (actor_type IN ('human', 'system')),
    actor_id TEXT NOT NULL,
    prior_reference_version_id TEXT NOT NULL REFERENCES reference_version(reference_version_id),
    new_reference_version_id TEXT NOT NULL REFERENCES reference_version(reference_version_id),
    impact_outcome TEXT NOT NULL CHECK (impact_outcome IN ('quarantine', 'revalidated', 'unaffected')),
    basis TEXT NOT NULL
) STRICT;

CREATE TABLE source_impact_subject (
    event_id TEXT NOT NULL REFERENCES source_impact_event(event_id),
    version_id TEXT NOT NULL REFERENCES question_version(version_id),
    question_id TEXT NOT NULL REFERENCES question_identity(question_id),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    impact_detail TEXT NOT NULL,
    PRIMARY KEY (event_id, version_id)
) STRICT;

CREATE VIEW latest_question_version AS
SELECT qv.*
FROM question_version AS qv
JOIN (
    SELECT question_id, MAX(version_number) AS version_number
    FROM question_version
    GROUP BY question_id
) AS latest
ON latest.question_id = qv.question_id
AND latest.version_number = qv.version_number;

CREATE VIEW ordered_decisive_review AS
SELECT
    re.*,
    ROW_NUMBER() OVER (
        PARTITION BY re.version_id
        ORDER BY re.recorded_at DESC, re.event_id DESC
    ) AS decision_rank
FROM review_event AS re
WHERE re.action IN ('approve', 'reject', 'revise', 'auto_invalidate');

CREATE VIEW exact_version_review_state AS
SELECT
    qv.question_id,
    qv.version_id,
    qv.version_number,
    qv.content_sha256,
    CASE WHEN latest.version_id IS NOT NULL THEN 1 ELSE 0 END AS is_latest_version,
    decisive.action AS latest_decisive_action,
    decisive.event_id AS latest_decisive_event_id
FROM question_version AS qv
LEFT JOIN latest_question_version AS latest ON latest.version_id = qv.version_id
LEFT JOIN ordered_decisive_review AS decisive
    ON decisive.version_id = qv.version_id
    AND decisive.decision_rank = 1;

CREATE VIEW verification_event_summary AS
SELECT
    ve.event_id,
    ve.recorded_at,
    ve.question_id,
    ve.version_id,
    ve.content_sha256,
    ve.required_check_set_id,
    COUNT(vc.check_id) AS check_count,
    SUM(CASE WHEN vc.outcome = 'pass' THEN 0 ELSE 1 END) AS nonpass_count
FROM verification_event AS ve
JOIN verification_check AS vc ON vc.event_id = ve.event_id
GROUP BY ve.event_id;

CREATE VIEW verification_policy_state AS
SELECT
    summary.*,
    CASE
        WHEN policy.required_check_set_id IS NOT NULL
         AND summary.check_count = policy.required_pass_count
         AND summary.nonpass_count = 0
         AND NOT EXISTS (
             SELECT 1
             FROM required_check_policy_item AS required
             WHERE required.required_check_set_id = summary.required_check_set_id
               AND NOT EXISTS (
                   SELECT 1
                   FROM verification_check AS observed
                   WHERE observed.event_id = summary.event_id
                     AND observed.check_id = required.check_id
               )
         )
        THEN 1 ELSE 0
    END AS policy_pass
FROM verification_event_summary AS summary
LEFT JOIN required_check_policy AS policy
    ON policy.required_check_set_id = summary.required_check_set_id;

CREATE VIEW ordered_verification_event AS
SELECT
    summary.*,
    ROW_NUMBER() OVER (
        PARTITION BY summary.version_id
        ORDER BY summary.recorded_at DESC, summary.event_id DESC
    ) AS verification_rank
FROM verification_policy_state AS summary;

CREATE VIEW ordered_source_impact_state AS
SELECT
    sis.version_id,
    sie.event_id,
    sie.recorded_at,
    sie.impact_outcome,
    ROW_NUMBER() OVER (
        PARTITION BY sis.version_id
        ORDER BY sie.recorded_at DESC, sie.event_id DESC
    ) AS impact_rank
FROM source_impact_subject AS sis
JOIN source_impact_event AS sie ON sie.event_id = sis.event_id;

CREATE VIEW learner_ready_projection AS
SELECT
    qv.question_id,
    qv.version_id,
    qv.version_number,
    qv.content_sha256,
    CASE WHEN latest.version_id IS NOT NULL THEN 1 ELSE 0 END AS is_latest_version,
    decisive.action AS latest_decisive_action,
    decisive.event_id AS latest_decisive_event_id,
    verification.event_id AS latest_verification_event_id,
    CASE
        WHEN verification.policy_pass = 1
        THEN 1 ELSE 0
    END AS mechanical_checks_pass,
    CASE
        WHEN impact.impact_outcome = 'quarantine' THEN 0 ELSE 1
    END AS source_impact_clear,
    CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM question_rule_trace AS trace
            JOIN rule_version AS rule ON rule.rule_version_id = trace.rule_version_id
            WHERE trace.version_id = qv.version_id
              AND json_extract(rule.content_json, '$.currency.assessment') <> 'current'
        ) THEN 1 ELSE 0
    END AS rules_current,
    CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM question_rule_trace AS trace
            JOIN rule_source_reference AS source_link ON source_link.rule_version_id = trace.rule_version_id
            JOIN reference_version AS reference ON reference.reference_version_id = source_link.reference_version_id
            WHERE trace.version_id = qv.version_id
              AND (
                  reference.record_purpose <> 'admitted_evidence'
                  OR json_extract(reference.record_json, '$.currency.assessment') <> 'current'
              )
        ) THEN 1 ELSE 0
    END AS references_admitted_current,
    CASE
        WHEN latest.version_id IS NOT NULL
         AND decisive.action = 'approve'
         AND decisive.actor_type = 'human'
         AND decisive.actor_id = 'james'
         AND verification.policy_pass = 1
         AND (impact.impact_outcome IS NULL OR impact.impact_outcome <> 'quarantine')
         AND json_extract(qv.content_json, '$.authorship.purpose') <> 'schema_fixture'
         AND NOT EXISTS (
             SELECT 1
             FROM question_rule_trace AS trace
             JOIN rule_version AS rule ON rule.rule_version_id = trace.rule_version_id
             WHERE trace.version_id = qv.version_id
               AND json_extract(rule.content_json, '$.currency.assessment') <> 'current'
         )
         AND NOT EXISTS (
             SELECT 1
             FROM question_rule_trace AS trace
             JOIN rule_source_reference AS source_link ON source_link.rule_version_id = trace.rule_version_id
             JOIN reference_version AS reference ON reference.reference_version_id = source_link.reference_version_id
             WHERE trace.version_id = qv.version_id
               AND (
                   reference.record_purpose <> 'admitted_evidence'
                   OR json_extract(reference.record_json, '$.currency.assessment') <> 'current'
               )
         )
        THEN 1 ELSE 0
    END AS learner_ready,
    CASE
        WHEN latest.version_id IS NOT NULL
         AND decisive.action = 'approve'
         AND decisive.actor_type = 'human'
         AND decisive.actor_id = 'james'
         AND verification.policy_pass = 1
         AND (impact.impact_outcome IS NULL OR impact.impact_outcome <> 'quarantine')
         AND json_extract(qv.content_json, '$.authorship.purpose') = 'production_candidate'
         AND NOT EXISTS (
             SELECT 1
             FROM question_rule_trace AS trace
             JOIN rule_version AS rule ON rule.rule_version_id = trace.rule_version_id
             WHERE trace.version_id = qv.version_id
               AND json_extract(rule.content_json, '$.currency.assessment') <> 'current'
         )
         AND NOT EXISTS (
             SELECT 1
             FROM question_rule_trace AS trace
             JOIN rule_source_reference AS source_link ON source_link.rule_version_id = trace.rule_version_id
             JOIN reference_version AS reference ON reference.reference_version_id = source_link.reference_version_id
             WHERE trace.version_id = qv.version_id
               AND (
                   reference.record_purpose <> 'admitted_evidence'
                   OR json_extract(reference.record_json, '$.currency.assessment') <> 'current'
               )
         )
        THEN 1 ELSE 0
    END AS coverage_contribution
FROM question_version AS qv
LEFT JOIN latest_question_version AS latest ON latest.version_id = qv.version_id
LEFT JOIN ordered_decisive_review AS decisive
    ON decisive.version_id = qv.version_id AND decisive.decision_rank = 1
LEFT JOIN ordered_verification_event AS verification
    ON verification.version_id = qv.version_id AND verification.verification_rank = 1
LEFT JOIN ordered_source_impact_state AS impact
    ON impact.version_id = qv.version_id AND impact.impact_rank = 1;

CREATE VIEW coverage_projection AS
SELECT
    readiness.version_id,
    mapping.mapping_ordinal,
    mapping.area_id,
    mapping.representative_task_id,
    readiness.coverage_contribution
FROM learner_ready_projection AS readiness
JOIN blueprint_mapping AS mapping ON mapping.version_id = readiness.version_id;

CREATE TRIGGER immutable_question_version_update
BEFORE UPDATE ON question_version BEGIN SELECT RAISE(ABORT, 'question versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_version_delete
BEFORE DELETE ON question_version BEGIN SELECT RAISE(ABORT, 'question versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_identity_update
BEFORE UPDATE ON question_identity BEGIN SELECT RAISE(ABORT, 'question identities are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_identity_delete
BEFORE DELETE ON question_identity BEGIN SELECT RAISE(ABORT, 'question identities are immutable projection inputs'); END;
CREATE TRIGGER immutable_reference_version_update
BEFORE UPDATE ON reference_version BEGIN SELECT RAISE(ABORT, 'reference versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_reference_version_delete
BEFORE DELETE ON reference_version BEGIN SELECT RAISE(ABORT, 'reference versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_rule_version_update
BEFORE UPDATE ON rule_version BEGIN SELECT RAISE(ABORT, 'rule versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_rule_version_delete
BEFORE DELETE ON rule_version BEGIN SELECT RAISE(ABORT, 'rule versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_rule_source_reference_update
BEFORE UPDATE ON rule_source_reference BEGIN SELECT RAISE(ABORT, 'rule source links are immutable projection inputs'); END;
CREATE TRIGGER immutable_rule_source_reference_delete
BEFORE DELETE ON rule_source_reference BEGIN SELECT RAISE(ABORT, 'rule source links are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_option_update
BEFORE UPDATE ON question_option BEGIN SELECT RAISE(ABORT, 'question options are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_option_delete
BEFORE DELETE ON question_option BEGIN SELECT RAISE(ABORT, 'question options are immutable projection inputs'); END;
CREATE TRIGGER immutable_blueprint_mapping_update
BEFORE UPDATE ON blueprint_mapping BEGIN SELECT RAISE(ABORT, 'blueprint mappings are immutable projection inputs'); END;
CREATE TRIGGER immutable_blueprint_mapping_delete
BEFORE DELETE ON blueprint_mapping BEGIN SELECT RAISE(ABORT, 'blueprint mappings are immutable projection inputs'); END;
CREATE TRIGGER immutable_difficulty_dimension_update
BEFORE UPDATE ON difficulty_dimension BEGIN SELECT RAISE(ABORT, 'difficulty dimensions are immutable projection inputs'); END;
CREATE TRIGGER immutable_difficulty_dimension_delete
BEFORE DELETE ON difficulty_dimension BEGIN SELECT RAISE(ABORT, 'difficulty dimensions are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_rule_trace_update
BEFORE UPDATE ON question_rule_trace BEGIN SELECT RAISE(ABORT, 'question rule traces are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_rule_trace_delete
BEFORE DELETE ON question_rule_trace BEGIN SELECT RAISE(ABORT, 'question rule traces are immutable projection inputs'); END;
CREATE TRIGGER append_only_review_event_update
BEFORE UPDATE ON review_event BEGIN SELECT RAISE(ABORT, 'review events are append-only projection inputs'); END;
CREATE TRIGGER append_only_review_event_delete
BEFORE DELETE ON review_event BEGIN SELECT RAISE(ABORT, 'review events are append-only projection inputs'); END;
CREATE TRIGGER append_only_verification_event_update
BEFORE UPDATE ON verification_event BEGIN SELECT RAISE(ABORT, 'verification events are append-only projection inputs'); END;
CREATE TRIGGER append_only_verification_event_delete
BEFORE DELETE ON verification_event BEGIN SELECT RAISE(ABORT, 'verification events are append-only projection inputs'); END;
CREATE TRIGGER append_only_verification_check_update
BEFORE UPDATE ON verification_check BEGIN SELECT RAISE(ABORT, 'verification checks are append-only projection inputs'); END;
CREATE TRIGGER append_only_verification_check_delete
BEFORE DELETE ON verification_check BEGIN SELECT RAISE(ABORT, 'verification checks are append-only projection inputs'); END;
CREATE TRIGGER append_only_source_impact_event_update
BEFORE UPDATE ON source_impact_event BEGIN SELECT RAISE(ABORT, 'source-impact events are append-only projection inputs'); END;
CREATE TRIGGER append_only_source_impact_event_delete
BEFORE DELETE ON source_impact_event BEGIN SELECT RAISE(ABORT, 'source-impact events are append-only projection inputs'); END;
CREATE TRIGGER append_only_source_impact_subject_update
BEFORE UPDATE ON source_impact_subject BEGIN SELECT RAISE(ABORT, 'source-impact subjects are append-only projection inputs'); END;
CREATE TRIGGER append_only_source_impact_subject_delete
BEFORE DELETE ON source_impact_subject BEGIN SELECT RAISE(ABORT, 'source-impact subjects are append-only projection inputs'); END;
