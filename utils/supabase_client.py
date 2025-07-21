import os
from supabase import create_client

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def get_or_create_user(first_name, email):
    supabase = get_supabase_client()
    try:
        res = supabase.table("users").select("id, first_name").eq("email", email).execute()
        if res.data and len(res.data) > 0:
            user_id = res.data[0]['id']
            if not res.data[0].get("first_name") or res.data[0].get("first_name") != first_name:
                supabase.table("users").update({"first_name": first_name}).eq("id", user_id).execute()
            return user_id
        else:
            insert_res = supabase.table("users").insert({"email": email, "first_name": first_name}).execute()
            if insert_res.data and len(insert_res.data) > 0:
                return insert_res.data[0]['id']
    except Exception as e:
        print(f"Error in get_or_create_user: {e}")
    return None

def save_tender_data(first_name, email, cpv, keyword, tenders):
    supabase = get_supabase_client()
    user_id = get_or_create_user(first_name, email)
    if not user_id:
        print("User creation failed")
        return None
    for tender in tenders:
        data = {
            "user_id": user_id,
            "cpv": cpv,
            "keyword": keyword,
            "tender_url": tender["url"],
            "criteria_summary": tender["summary"],
        }
        try:
            supabase.table("tenders").insert(data).execute()
        except Exception as e:
            print(f"Error saving tender: {e}")
    return user_id

# Example function for fetching pending jobs, adapt as you need
def get_pending_weekly_emails():
    # Replace with logic to query users needing an email and their tenders
    return []
