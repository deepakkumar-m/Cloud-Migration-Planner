import streamlit as st
import re
import time
import requests  # For future Gemini API integration

# Function to generate migration plan dynamically
def generate_migration_plan(input_data, cloud_provider="AWS"):
    # Parse input dynamically (unchanged)
    try:
        vms = int(re.search(r'(\d+)\s*VMs?', input_data, re.IGNORECASE).group(1) or 0)
    except AttributeError:
        vms = 0
    try:
        dbs = int(re.search(r'(\d+)\s*(database|DB)s?', input_data, re.IGNORECASE).group(1) or 0)
    except AttributeError:
        dbs = 0
    try:
        storage_match = re.search(r'(\d+)\s*(TB|GB)', input_data, re.IGNORECASE)
        storage = int(storage_match.group(1)) if storage_match else 0
        storage_unit = storage_match.group(2) if storage_match else "TB"
    except AttributeError:
        storage, storage_unit = 0, "TB"

    if vms == 0 and dbs == 0 and storage == 0:
        return "Error: Please provide valid input (e.g., '10 VMs, 2 databases, 5TB storage')."

    # Dynamic cloud service mapping
    service_map = {
        "AWS": {"vm": "EC2", "db": "RDS", "storage": "S3"},
        "Azure": {"vm": "Virtual Machines", "db": "Azure SQL Database", "storage": "Blob Storage"},
        "GCP": {"vm": "Compute Engine (GCE)", "db": "Cloud SQL", "storage": "Cloud Storage (GCS)"}
    }
    vm_service = service_map[cloud_provider]["vm"]
    db_service = service_map[cloud_provider]["db"]
    storage_service = service_map[cloud_provider]["storage"]

    # Calculations (unchanged)
    vm_cost = vms * 100
    db_cost = dbs * 500
    storage_cost = storage * (20 if storage_unit == "TB" else 0.02)
    total_cost = vm_cost + db_cost + storage_cost
    timeline = max(1, (vms + dbs) // 20)

    # Updated plan with correct service names
    plan = f"""
    ### Migration Plan for {cloud_provider}
    **Input Analysis**: {vms} VMs, {dbs} databases, {storage} {storage_unit} storage.

    1. **Assessment**: 
       - Identified {vms} VMs, {dbs} databases, {storage} {storage_unit} of storage.
    2. **Cloud Mapping**: 
       - VMs → {vm_service}
       - Databases → {db_service}
       - Storage → {storage_service}
    3. **Timeline**: {timeline} month(s) for migration and testing.
    4. **Risks & Mitigations**: 
       - {'High' if vms > 50 else 'Low'} risk of VM scaling issues; use auto-scaling groups.
       - {'High' if dbs > 3 else 'Low'} risk of database downtime; implement replication.
       - {'High' if storage > 20 else 'Low'} risk of data transfer delays; use incremental backups.
    5. **Cost Estimate**: Approximately ${total_cost:,}/month on {cloud_provider}.
    """
    return plan

# Placeholder for Gemini API integration
def generate_migration_plan_gemini(input_data, cloud_provider="AWS"):
    api_key = ""  # Replace with your key
    url = "https://api.gemini.com/v1/generate"  # Replace with actual endpoint
    prompt = f"""
    Generate a detailed cloud migration plan for the following on-premises setup:
    {input_data}
    Target cloud: {cloud_provider}
    Include:
    1. Assessment of infrastructure
    2. Cloud service mappings
    3. Timeline
    4. Risks and mitigations
    5. Rough cost estimate
    """

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        return response.json()["text"]  # Adjust based on API response
    except requests.exceptions.RequestException as e:
        return f"Error: Could not generate plan. API issue: {str(e)}"

# Streamlit UI
st.title("Cloud Migration Planner")

# Input form
st.header("Describe Your On-Premises Setup")
cloud_provider = st.selectbox("Select Cloud Provider", ["AWS", "Azure", "GCP"], index=0)
user_input = st.text_area(
    "Enter details (e.g., '10 VMs, 2 databases, 5TB storage'):", 
    "50 VMs, 2 databases, 10TB storage",
    help="Specify number of VMs, databases, and storage (e.g., '5 VMs, 1 DB, 2TB')."
)

# Button to generate plan
if st.button("Generate Migration Plan"):
    with st.spinner("Generating plan..."):
        time.sleep(1)  # Simulate processing delay
        # Use generate_migration_plan for simulation
        # Replace with generate_migration_plan_gemini when API is ready
        plan = generate_migration_plan(user_input, cloud_provider)
        
        st.markdown("---")
        st.header("Your Migration Plan")
        if "Error" in plan:
            st.error(plan)
        else:
            st.markdown(plan)

# Download option
if 'plan' in locals() and "Error" not in plan:
    st.download_button(
        label="Download Plan",
        data=plan,
        file_name=f"migration_plan_{cloud_provider}.md",
        mime="text/markdown"
    )

# Footer
st.markdown("Powered by GenAI & Streamlit")
