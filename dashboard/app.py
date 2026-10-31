
from pathlib import Path
import sys
import json
import tempfile
import zipfile

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from directory_analyzer import analyze_directory
from regression_detector import resource_map
from upgrade_risk_comparator import compare_upgrade


st.set_page_config(
    page_title="Terraform Security Analyzer",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}
.block-container {
    padding-top: 2rem;
}
[data-testid="stMetric"] {
    background: #1c2330;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #303846;
}
div.stButton > button {
    width: 100%;
    border-radius: 8px;
    height: 48px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def extract_zip(uploaded_file, destination):
    destination = Path(destination).resolve()

    with zipfile.ZipFile(uploaded_file) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue

            target = (destination / member.filename).resolve()

            if target != destination and destination not in target.parents:
                raise ValueError("Unsafe ZIP archive path detected.")

            archive.extract(member, destination)

    if not list(destination.rglob("*.tf")):
        raise ValueError("ZIP archive does not contain Terraform .tf files.")

    return destination


def analyze_upgrade(old_dir, new_dir):
    old_actions, old_trust = analyze_directory(old_dir)
    new_actions, new_trust = analyze_directory(new_dir)

    old_resources = resource_map(old_dir)
    new_resources = resource_map(new_dir)

    added_actions = sorted(new_actions - old_actions)
    removed_actions = sorted(old_actions - new_actions)

    added_trust = sorted(new_trust - old_trust)
    removed_trust = sorted(old_trust - new_trust)

    resource_changes = []

    for key in sorted(set(old_resources) | set(new_resources)):
        old_record = old_resources.get(key)
        new_record = new_resources.get(key)

        old_set = old_record["actions"] if old_record else set()
        new_set = new_record["actions"] if new_record else set()

        added = sorted(new_set - old_set)
        removed = sorted(old_set - new_set)

        if added or removed:
            evidence = new_record or old_record

            resource_changes.append({
                "resource": f"{key[0]}.{key[1]}",
                "added_actions": added,
                "removed_actions": removed,
                "evidence_file": str(evidence["file"])
            })

    risk_result = compare_upgrade(old_dir, new_dir)

    if risk_result["introduced"]:
        risk_level = "High"
    elif added_actions or added_trust:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "added_actions": added_actions,
        "removed_actions": removed_actions,
        "added_trust": [list(edge) for edge in added_trust],
        "removed_trust": [list(edge) for edge in removed_trust],
        "resource_changes": resource_changes,
        "risk_findings": {
            category: [
                {
                    "role": item["role"],
                    "policy": item["policy"],
                    "finding": item["finding"],
                    "evidence": item.get("evidence", []),
                    "confidence": item.get("confidence", "")
                }
                for item in risk_result[category]
            ]
            for category in ("introduced", "removed", "unchanged")
        }
    }


# Sidebar
with st.sidebar:
    st.title("🛡️ Terraform Analyzer")
    st.caption("Security Impact Analysis")
    st.divider()
    st.markdown("### Analysis modules")
    st.markdown("- IAM permission comparison")
    st.markdown("- Trust relationship analysis")
    st.markdown("- Resource-level changes")
    st.markdown("- Policy-version risk detection")
    st.divider()
    st.caption("Static analysis prototype")


# Main header
st.title("Terraform Upgrade Security Analyzer")
st.markdown(
    "Identify security-sensitive changes between Terraform module versions "
    "before cloud deployment."
)

st.info(
    "Upload the old and new Terraform configuration as ZIP files. "
    "The analyzer performs local static analysis; no AWS deployment is performed."
)

st.divider()

# Upload section
st.subheader("1. Upload Terraform configurations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Old version")
    old_zip = st.file_uploader(
        "Upload old Terraform ZIP",
        type=["zip"],
        key="old_zip"
    )

with col2:
    st.markdown("#### New version")
    new_zip = st.file_uploader(
        "Upload new Terraform ZIP",
        type=["zip"],
        key="new_zip"
    )

st.caption(
    "Each ZIP should contain Terraform .tf files. "
    "You can ZIP a folder containing multiple Terraform files."
)

st.divider()

# Analysis
st.subheader("2. Run security analysis")

if st.button("🔍 Analyze Terraform Upgrade", type="primary"):
    if old_zip is None or new_zip is None:
        st.error("Please upload both old and new Terraform ZIP files.")

    else:
        try:
            with st.spinner("Analyzing Terraform configurations..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)

                    old_dir = extract_zip(
                        old_zip,
                        temp_path / "old"
                    )

                    new_dir = extract_zip(
                        new_zip,
                        temp_path / "new"
                    )

                    report = analyze_upgrade(old_dir, new_dir)

            st.session_state["analysis_report"] = report
            st.success("Terraform upgrade analysis completed!")

        except zipfile.BadZipFile:
            st.error("Invalid ZIP file. Please upload valid ZIP archives.")

        except Exception as error:
            st.error(f"Analysis failed: {error}")


# Results
if "analysis_report" in st.session_state:
    report = st.session_state["analysis_report"]

    st.divider()
    st.subheader("3. Security analysis results")

    risk_colors = {
        "High": "🔴",
        "Medium": "🟠",
        "Low": "🟢"
    }

    st.markdown(
        f"### {risk_colors[report['risk_level']]} "
        f"Overall risk indicator: {report['risk_level']}"
    )

    st.caption(
        "Prototype prioritization based on implemented detection rules; "
        "not a verified exploitability assessment."
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Added IAM actions",
        len(report["added_actions"])
    )

    metric2.metric(
        "Removed IAM actions",
        len(report["removed_actions"])
    )

    metric3.metric(
        "Trust changes",
        len(report["added_trust"]) + len(report["removed_trust"])
    )

    metric4.metric(
        "Resource changes",
        len(report["resource_changes"])
    )

    # IAM changes
    st.subheader("IAM permission changes")

    tab1, tab2 = st.tabs(["Added permissions", "Removed permissions"])

    with tab1:
        if report["added_actions"]:
            for action in report["added_actions"]:
                st.error(f"+ {action}")
        else:
            st.success("No added IAM actions detected.")

    with tab2:
        if report["removed_actions"]:
            for action in report["removed_actions"]:
                st.info(f"- {action}")
        else:
            st.write("No removed IAM actions detected.")

    # Trust relationships
    st.subheader("Trust relationship changes")

    trust_col1, trust_col2 = st.columns(2)

    with trust_col1:
        st.markdown("**Added relationships**")
        if report["added_trust"]:
            for source, target in report["added_trust"]:
                st.warning(f"{source} → {target}")
        else:
            st.write("None")

    with trust_col2:
        st.markdown("**Removed relationships**")
        if report["removed_trust"]:
            for source, target in report["removed_trust"]:
                st.info(f"{source} → {target}")
        else:
            st.write("None")

    # Resource-level changes
    st.subheader("Resource-level IAM changes")

    if report["resource_changes"]:
        st.dataframe(
            report["resource_changes"],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No resource-level IAM action changes detected.")

    # Policy risk
    st.subheader("Policy-version risk findings")

    risk_tabs = st.tabs([
        "Introduced",
        "Removed",
        "Unchanged"
    ])

    for tab, category in zip(
        risk_tabs,
        ("introduced", "removed", "unchanged")
    ):
        with tab:
            findings = report["risk_findings"][category]

            if not findings:
                st.write("No findings in this category.")

            for finding in findings:
                with st.expander(
                    f"{finding['finding']} — {finding['role']}"
                ):
                    st.write("**Role:**", finding["role"])
                    st.write("**Policy:**", finding["policy"])
                    st.write("**Evidence actions:**")
                    st.code(
                        "\n".join(finding["evidence"]) or "Not available"
                    )
                    st.caption(finding["confidence"])

    # Download report
    st.divider()
    st.subheader("4. Export security report")

    report_json = json.dumps(report, indent=4)

    st.download_button(
        label="⬇️ Download JSON Security Report",
        data=report_json,
        file_name="terraform_security_report.json",
        mime="application/json"
    )

    st.warning(
        "Findings are static-analysis candidates. "
        "They do not prove that a privilege-escalation path is exploitable."
    )
