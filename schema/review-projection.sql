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

CREATE TRIGGER immutable_question_version_update
BEFORE UPDATE ON question_version BEGIN SELECT RAISE(ABORT, 'question versions are immutable projection inputs'); END;
CREATE TRIGGER immutable_question_version_delete
BEFORE DELETE ON question_version BEGIN SELECT RAISE(ABORT, 'question versions are immutable projection inputs'); END;
CREATE TRIGGER append_only_review_event_update
BEFORE UPDATE ON review_event BEGIN SELECT RAISE(ABORT, 'review events are append-only projection inputs'); END;
CREATE TRIGGER append_only_review_event_delete
BEFORE DELETE ON review_event BEGIN SELECT RAISE(ABORT, 'review events are append-only projection inputs'); END;
CREATE TRIGGER append_only_verification_event_update
BEFORE UPDATE ON verification_event BEGIN SELECT RAISE(ABORT, 'verification events are append-only projection inputs'); END;
CREATE TRIGGER append_only_verification_event_delete
BEFORE DELETE ON verification_event BEGIN SELECT RAISE(ABORT, 'verification events are append-only projection inputs'); END;
CREATE TRIGGER append_only_source_impact_event_update
BEFORE UPDATE ON source_impact_event BEGIN SELECT RAISE(ABORT, 'source-impact events are append-only projection inputs'); END;
CREATE TRIGGER append_only_source_impact_event_delete
BEFORE DELETE ON source_impact_event BEGIN SELECT RAISE(ABORT, 'source-impact events are append-only projection inputs'); END;
