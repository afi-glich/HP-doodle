"""Add database functions

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Get best full-day slot function
    op.execute("""
    CREATE OR REPLACE FUNCTION get_best_full_day_slot(event_id_param INTEGER)
    RETURNS TABLE (
        slot_id INTEGER,
        slot_date DATE,
        available_count INTEGER,
        maybe_count INTEGER,
        unavailable_count INTEGER,
        score NUMERIC
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            fds.id,
            fds.slot_date,
            COUNT(CASE WHEN fdp.preference = 'AVAILABLE' THEN 1 END)::INTEGER as available_count,
            COUNT(CASE WHEN fdp.preference = 'MAYBE' THEN 1 END)::INTEGER as maybe_count,
            COUNT(CASE WHEN fdp.preference = 'UNAVAILABLE' THEN 1 END)::INTEGER as unavailable_count,
            (COUNT(CASE WHEN fdp.preference = 'AVAILABLE' THEN 1 END)::numeric * 2 + 
             COUNT(CASE WHEN fdp.preference = 'MAYBE' THEN 1 END)::numeric)::NUMERIC as score
        FROM full_day_slots fds
        LEFT JOIN full_day_preferences fdp ON fds.id = fdp.slot_id
        WHERE fds.event_id = event_id_param
        GROUP BY fds.id, fds.slot_date
        ORDER BY score DESC, available_count DESC
        LIMIT 1;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Get best time-based slot function
    op.execute("""
    CREATE OR REPLACE FUNCTION get_best_time_based_slot(event_id_param INTEGER)
    RETURNS TABLE (
        slot_id INTEGER,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        available_count INTEGER,
        maybe_count INTEGER,
        unavailable_count INTEGER,
        score NUMERIC
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            tbs.id,
            tbs.start_time,
            tbs.end_time,
            COUNT(CASE WHEN tbp.preference = 'AVAILABLE' THEN 1 END)::INTEGER as available_count,
            COUNT(CASE WHEN tbp.preference = 'MAYBE' THEN 1 END)::INTEGER as maybe_count,
            COUNT(CASE WHEN tbp.preference = 'UNAVAILABLE' THEN 1 END)::INTEGER as unavailable_count,
            (COUNT(CASE WHEN tbp.preference = 'AVAILABLE' THEN 1 END)::numeric * 2 + 
             COUNT(CASE WHEN tbp.preference = 'MAYBE' THEN 1 END)::numeric)::NUMERIC as score
        FROM time_based_slots tbs
        LEFT JOIN time_based_preferences tbp ON tbs.id = tbp.slot_id
        WHERE tbs.event_id = event_id_param
        GROUP BY tbs.id, tbs.start_time, tbs.end_time
        ORDER BY score DESC, available_count DESC
        LIMIT 1;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Check and finalize event function
    op.execute("""
    CREATE OR REPLACE FUNCTION check_and_finalize_event(event_id_param INTEGER)
    RETURNS BOOLEAN AS $$
    DECLARE
        event_row events%ROWTYPE;
        total_invited INTEGER;
        total_responded INTEGER;
        response_percentage NUMERIC;
        best_slot_id INTEGER;
    BEGIN
        SELECT * INTO event_row FROM events WHERE id = event_id_param;
        
        IF event_row.id IS NULL OR event_row.finalized THEN
            RETURN FALSE;
        END IF;
        
        SELECT COUNT(*) INTO total_invited FROM event_participants 
        WHERE event_id = event_id_param AND status = 'ACCEPTED';
        
        SELECT COUNT(*) INTO total_responded FROM event_participants 
        WHERE event_id = event_id_param AND responded_at IS NOT NULL;
        
        IF total_invited = 0 THEN
            RETURN FALSE;
        END IF;
        
        response_percentage := (total_responded::numeric / total_invited::numeric) * 100;
        
        IF response_percentage >= event_row.min_quorum_percentage THEN
            IF event_row.event_type = 'FULL_DAY' THEN
                SELECT slot_id INTO best_slot_id FROM get_best_full_day_slot(event_id_param) LIMIT 1;
            ELSE
                SELECT slot_id INTO best_slot_id FROM get_best_time_based_slot(event_id_param) LIMIT 1;
            END IF;
            
            UPDATE events 
            SET finalized = TRUE, 
                final_slot_id = best_slot_id,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = event_id_param;
            
            INSERT INTO event_activity_log (event_id, action, description)
            VALUES (event_id_param, 'EVENT_FINALIZED', 
                    'Event finalized with best slot: ' || COALESCE(best_slot_id::text, 'None'));
            
            RETURN TRUE;
        END IF;
        
        RETURN FALSE;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Update preference function
    op.execute("""
    CREATE OR REPLACE FUNCTION update_preference_and_check(
        participant_id_param INTEGER,
        slot_id_param INTEGER,
        preference_param availability_preference,
        is_full_day BOOLEAN
    )
    RETURNS BOOLEAN AS $$
    DECLARE
        event_id_param INTEGER;
    BEGIN
        IF is_full_day THEN
            SELECT event_id INTO event_id_param FROM full_day_slots WHERE id = slot_id_param;
            
            INSERT INTO full_day_preferences (slot_id, participant_id, preference)
            VALUES (slot_id_param, participant_id_param, preference_param)
            ON CONFLICT (slot_id, participant_id) DO UPDATE
            SET preference = preference_param, updated_at = CURRENT_TIMESTAMP;
        ELSE
            SELECT event_id INTO event_id_param FROM time_based_slots WHERE id = slot_id_param;
            
            INSERT INTO time_based_preferences (slot_id, participant_id, preference)
            VALUES (slot_id_param, participant_id_param, preference_param)
            ON CONFLICT (slot_id, participant_id) DO UPDATE
            SET preference = preference_param, updated_at = CURRENT_TIMESTAMP;
        END IF;
        
        UPDATE event_participants
        SET responded_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = participant_id_param;
        
        RETURN check_and_finalize_event(event_id_param);
    END;
    $$ LANGUAGE plpgsql;
    """)


def downgrade():
    op.execute("DROP FUNCTION IF EXISTS update_preference_and_check(INTEGER, INTEGER, availability_preference, BOOLEAN)")
    op.execute("DROP FUNCTION IF EXISTS check_and_finalize_event(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS get_best_time_based_slot(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS get_best_full_day_slot(INTEGER)")
