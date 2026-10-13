CREATE OR REPLACE FUNCTION enforce_sibling_name_uniqueness()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_advisory_xact_lock(
        hashtextextended(NEW.parent_id::text || ':' || lower(NEW.name), 0));

    IF TG_TABLE_NAME = 'folders' AND EXISTS (
        SELECT 1 FROM files
        WHERE parent_id = NEW.parent_id AND lower(name) = lower(NEW.name)
    ) THEN
        RAISE EXCEPTION 'An entry with this name already exists in the folder.'
            USING ERRCODE = '23505', CONSTRAINT = 'uq_entries_parent_name';
    END IF;

    IF TG_TABLE_NAME = 'files' AND EXISTS (
        SELECT 1 FROM folders
        WHERE parent_id = NEW.parent_id AND lower(name) = lower(NEW.name)
    ) THEN
        RAISE EXCEPTION 'An entry with this name already exists in the folder.'
            USING ERRCODE = '23505', CONSTRAINT = 'uq_entries_parent_name';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER folders_sibling_name_uniqueness
    BEFORE INSERT OR UPDATE OF parent_id, name ON folders
    FOR EACH ROW EXECUTE FUNCTION enforce_sibling_name_uniqueness();

CREATE TRIGGER files_sibling_name_uniqueness
    BEFORE INSERT OR UPDATE OF parent_id, name ON files
    FOR EACH ROW EXECUTE FUNCTION enforce_sibling_name_uniqueness();
