
from memory.database import (
    get_connection,
    initialize_database
)


def save_claim(claim, decision):
    """
    Save a submitted research claim and its final decision.
    Returns the ID of the saved claim.
    """

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO claim_history (
                claim,
                verdict,
                confidence,
                explanation
            )
            VALUES (?, ?, ?, ?)
        """, (
            claim,
            decision.get("verdict"),
            decision.get("confidence"),
            decision.get("explanation")
        ))

        claim_id = cursor.lastrowid

        connection.commit()

        return claim_id

    finally:
        connection.close()


def save_evidence(claim_id, evaluated_evidence):
    """
    Save evaluated research publications
    associated with a particular claim.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        for evidence in evaluated_evidence:

            assessment = evidence.get(
                "evidence_assessment",
                evidence.get("assessment", evidence)
            )

            cursor.execute("""
                INSERT INTO evidence_records (
                    claim_id,
                    publication_id,
                    title,
                    year,
                    doi,
                    classification,
                    relevance,
                    study_type,
                    findings_status,
                    evidence_strength,
                    explanation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim_id,
                evidence.get("publication_id"),
                evidence.get("title"),
                evidence.get("year"),
                evidence.get("doi"),
                assessment.get("classification"),
                assessment.get("relevance"),
                assessment.get("study_type"),
                assessment.get("findings_status"),
                assessment.get("evidence_strength"),
                assessment.get("explanation")
            ))

        connection.commit()

    finally:
        connection.close()


def get_claim_history(limit=10):
    """
    Retrieve the most recent verification cases.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM claim_history
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """, (limit,))

        records = [
            dict(row) for row in cursor.fetchall()
        ]

        return records

    finally:
        connection.close()


def get_claim_details(claim_id):
    """
    Retrieve a claim together with its research evidence.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM claim_history
            WHERE id = ?
        """, (claim_id,))

        claim = cursor.fetchone()

        if claim is None:
            return None

        cursor.execute("""
            SELECT *
            FROM evidence_records
            WHERE claim_id = ?
        """, (claim_id,))

        evidence = [
            dict(row) for row in cursor.fetchall()
        ]

        return {
            "claim": dict(claim),
            "evidence": evidence
        }

    finally:
        connection.close()


def save_feedback(claim_id, user_feedback):
    """
    Save user feedback associated with a previous claim.
    """

    if not user_feedback or not user_feedback.strip():
        raise ValueError("Feedback cannot be empty.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO feedback (
                claim_id,
                user_feedback
            )
            VALUES (?, ?)
        """, (claim_id, user_feedback.strip()))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def search_similar_claims(claim, limit=5):
    """
    Search previous verification cases using
    SQLite text matching.

    This is keyword matching, not semantic similarity.
    """

    if not claim or not claim.strip():
        return []

    if limit < 1:
        return []

    connection = get_connection()

    try:
        cursor = connection.cursor()

        search_term = f"%{claim.strip()}%"

        cursor.execute("""
            SELECT *
            FROM claim_history
            WHERE claim LIKE ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """, (search_term, limit))

        results = [
            dict(row) for row in cursor.fetchall()
        ]

        return results

    finally:
        connection.close()

def get_feedback(claim_id):
    """
    Retrieve all feedback associated with a verification case.
    """

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, claim_id, user_feedback, created_at
            FROM feedback
            WHERE claim_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (claim_id,)
        )

        results = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return results

    finally:
        connection.close()

if __name__ == "__main__":

    initialize_database()

    print("VERIAGENT MEMORY SYSTEM")
    print("=" * 45)
    print("Memory functions initialized successfully!")
    print("Available functions:")
    print("- save_claim()")
    print("- save_evidence()")
    print("- get_claim_history()")
    print("- get_claim_details()")
    print("- save_feedback()")
    print("- search_similar_claims()")
