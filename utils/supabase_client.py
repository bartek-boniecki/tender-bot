import os
from supabase import create_client

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    print(f"Supabase URL: {url}, Key length: {len(key) if key else 0}")
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY")
    return create_client(url, key)

def get_or_create_user(first_name, email):
    supabase = get_supabase_client()
    # Try to find user by email
    try:
        res = supabase.table("users").select("id, first_name").eq("email", email).execute()
        if res.data and len(res.data) > 0:
            user_id = res.data[0]['id']
            # Update first_name if not set or different
            if not res.data[0].get("first_name") or res.data[0].get("first_name") != first_name:
                supabase.table("users").update({"first_name": first_name}).eq("id", user_id).execute()
            print(f"Found existing user_id for email {email}: {user_id}")
            return user_id
        else:
            # If not found, insert new user
            insert_res = supabase.table("users").insert({"email": email, "first_name": first_name}).execute()
            if insert_res.data and len(insert_res.data) > 0:
                user_id = insert_res.data[0]['id']
                print(f"Created new user_id for email {email}: {user_id}")
                return user_id
            else:
                print(f"Failed to create user for email {email}")
                return None
    except Exception as e:
        print(f"Error in get_or_create_user: {e}")
        return None

def save_tender_data(first_name, email, cpv, keyword, tenders):
    supabase = get_supabase_client()
    user_id = get_or_create_user(first_name, email)
    if not user_id:
        print(f"Cannot save tenders, user_id not found or created for email {email}")
        return
    for tender in tenders:
        data = {
            "user_id": user_id,
            "cpv": cpv,
            "keyword": keyword,
            "tender_url": tender["url"],
            "criteria_summary": tender["summary"],
        }
        print(f"Saving tender: {data}")
        try:
            result = supabase.table("tenders").insert(data).execute()
            print(f"Supabase insert result: {result}")
        except Exception as e:
            print(f"Error saving tender to Supabase: {e}")

def save_user_email(email):
    # This function is now optional, since get_or_create_user does the work!
    return
