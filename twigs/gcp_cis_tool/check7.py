import sys
import json
import logging
import gcp_cis_utils

def check7_1():
    # 7.1 Ensure that BigQuery datasets are not anonymously or publicly accessible (Scored)

    logging.info("7.1 Ensure that BigQuery datasets are not anonymously or publicly accessible (Scored)")
    details = []
    projects = gcp_cis_utils.get_bigquery_enabled_projects()
    for p in projects:
        output = gcp_cis_utils.run_cmd("bq ls --project_id=%s --format=json 2>/dev/null" % p)
        out_json = json.loads(output)
        for entry in out_json:
            if entry['kind'] != "bigquery#dataset":
                continue
            dataset_id = entry['id']
            output = gcp_cis_utils.run_cmd("bq show --format=json %s 2>/dev/null" %dataset_id)
            out_json_2 = json.loads(output) 
            access_configs = out_json_2.get('access')
            if access_configs is not None:
                for ac in access_configs:
                    if ac.get('specialGroup') == "allAuthenticatedUsers" or ac.get('iamMember') == "allUsers":
                        details.append("BigQuery dataset [%s] in project [%s] is anonymously or publicly accessible" % (dataset_id.split(':')[1], p))
                        break
    if len(details) > 0:
        return gcp_cis_utils.create_issue('cis-gcp-bench-check-7.1', '7.1 [Level 1] Ensure that BigQuery datasets are not anonymously or publicly accessible (Scored)', "\n".join(details), '4', '', '')
    return None

def run_checks():
    config_issues = []
    gcp_cis_utils.append_issue(config_issues, check7_1())
    return config_issues

