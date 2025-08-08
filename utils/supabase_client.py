import os
from supabase import create_client

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def get_or_create_user(first_name: str, email: str) -> int | None:
    """
    Only ensures a user record exists (id, first_name, email).
    Returns the user_id.
    """
    supabase = get_supabase_client()
    try:
        res = (
            supabase.table("users")
            .select("id, first_name, email")
            .eq("email", email)
            .execute()
        )
        if res.data and len(res.data) > 0:
            user = res.data[0]
            user_id = user["id"]
            # Update first_name if it has changed
            if user.get("first_name") != first_name:
                supabase.table("users").update(
                    {"first_name": first_name}
                ).eq("id", user_id).execute()
            return user_id

        # Insert new user
        insert_res = (
            supabase.table("users")
            .insert({"email": email, "first_name": first_name})
            .execute()
        )
        if insert_res.data and len(insert_res.data) > 0:
            return insert_res.data[0]["id"]

    except Exception as e:
        print(f"Error in get_or_create_user: {e}")
    return None

def save_tender_data(
    first_name: str,
    email: str,
    cpv: str,
    keyword: str,
    tenders: list[dict]
) -> list[dict]:
    """
    Inserts only new tenders into supabase.tenders, storing cpv+keyword
    on each tender. Returns the list of newly added tenders.
    """
    supabase = get_supabase_client()
    user_id = get_or_create_user(first_name, email)
    if not user_id:
        print("User creation failed")
        return []

    new_tenders = []
    for tender in tenders:
        url = tender.get("url")
        try:
            exists = (
                supabase.table("tenders")
                .select("id")
                .eq("user_id", user_id)
                .eq("tender_url", url)
                .execute()
            )
            if not exists.data:
                rec = {
                    "user_id": user_id,
                    "cpv": cpv,
                    "keyword": keyword,
                    "tender_url": url,
                    "criteria_summary": tender.get("summary", "")
                }
                supabase.table("tenders").insert(rec).execute()
                new_tenders.append(tender)
        except Exception as e:
            print(f"Error saving tender {url}: {e}")

    return new_tenders

def get_all_users() -> list[dict]:
    """
    Returns a list of all users with id, first_name, email.
    """
    supabase = get_supabase_client()
    try:
        res = (
            supabase.table("users")
            .select("id, first_name, email")
            .execute()
        )
        return res.data or []
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def get_user_preferences(user_id: int) -> tuple[str | None, str | None]:
    """
    Grabs the most‐recent cpv & keyword from tenders table for this user.
    """
    supabase = get_supabase_client()
    try:
        res = (
            supabase.table("tenders")
            .select("cpv, keyword")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            row = res.data[0]
            return row.get("cpv"), row.get("keyword")
    except Exception as e:
        print(f"Error fetching preferences for user {user_id}: {e}")
    return None, None
