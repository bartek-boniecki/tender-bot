import os
from supabase import create_client

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def get_or_create_user(first_name, email, keyword, cpv):
    supabase = get_supabase_client()
    try:
        res = supabase.table("users") \
            .select("id, first_name, keyword, cpv") \
            .eq("email", email) \
            .execute()

        if res.data and len(res.data) > 0:
            user = res.data[0]
            user_id = user['id']
            update_data = {}
            if user.get("first_name") != first_name:
                update_data["first_name"] = first_name
            if user.get("keyword") != keyword:
                update_data["keyword"] = keyword
            if user.get("cpv") != cpv:
                update_data["cpv"] = cpv
            if update_data:
                supabase.table("users").update(update_data).eq("id", user_id).execute()
            return user_id

        # no existing user → create
        insert_res = supabase.table("users") \
            .insert({
                "email": email,
                "first_name": first_name,
                "keyword": keyword,
                "cpv": cpv
            }).execute()
        if insert_res.data and len(insert_res.data) > 0:
            return insert_res.data[0]['id']

    except Exception as e:
        print(f"Error in get_or_create_user: {e}")
    return None

def save_tender_data(first_name, email, cpv, keyword, tenders):
    """
    Inserts only *new* tenders into supabase.tenders.
    Returns the list of tenders that were newly added.
    """
    supabase = get_supabase_client()
    user_id = get_or_create_user(first_name, email, keyword, cpv)
    if not user_id:
        print("User creation failed")
        return []

    new_tenders = []
    for tender in tenders:
        url = tender.get("url")
        try:
            exists = supabase.table("tenders") \
                .select("id") \
                .eq("user_id", user_id) \
                .eq("tender_url", url) \
                .execute()

            if not exists.data:
                data = {
                    "user_id": user_id,
                    "cpv": cpv,
                    "keyword": keyword,
                    "tender_url": url,
                    "criteria_summary": tender.get("summary", "")
                }
                supabase.table("tenders").insert(data).execute()
                new_tenders.append(tender)

        except Exception as e:
            print(f"Error saving tender {url}: {e}")

    return new_tenders

def get_all_users():
    supabase = get_supabase_client()
    try:
        res = supabase.table("users") \
            .select("id, first_name, email, keyword, cpv") \
            .execute()
        return res.data or []
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
