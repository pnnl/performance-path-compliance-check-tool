
import json
import csv

output_name = "sys_7_raw_output"
csv_name = f"{output_name}"

output_json = open (
    f"C:\\git\\ruleset-checking-tool\\examples\\output\{output_name}.json")

output_csv_path = f"C:\\git\\ruleset-checking-tool\\examples\\output\{csv_name}.csv"

output_dict = json.load(output_json)


def parse_result_dictionary(output, n_passed, n_failed, n_undetermined, message):

    for result_dict in output["result"]:

        if isinstance(result_dict, str):

            if output["result"] == "PASS":
                n_passed += 1
            elif output["result"] == "FAILED":
                n_failed += 1
            elif output["result"] == "UNDETERMINED":
                n_undetermined += 1
                if message is None:
                    message = output["message"]

            break

        # If results are a list rather than flat dictionary, recursively search each result and update counts
        elif isinstance(result_dict["result"], list):

            n_passed, n_failed, n_undetermined, message = parse_result_dictionary(result_dict, n_passed, n_failed, n_undetermined, message)

        else:

            if result_dict["result"] == "PASS":
                n_passed += 1
            elif result_dict["result"] == "FAILED":
                n_failed += 1
            elif result_dict["result"] == "UNDETERMINED":
                n_undetermined += 1
                if message is None:
                    message = result_dict["message"]

    return n_passed, n_failed, n_undetermined, message


with open(output_csv_path, 'w', newline='') as file:

    writer = csv.writer(file)

    # Write headers
    writer.writerow(["Rule ID", "Ruleset Reference", "Rule Description", "Primary Rule", "Outcome", "N_Pass", "N_Fail", "N_Undetermined", "Message"])

    for output in output_dict:

        rule_id = output["id"]
        n_passed = 0
        n_failed = 0
        n_undetermined = 0
        n_not_applicable = 0
        message = None

        # Parse and update results
        n_passed, n_failed, n_undetermined, message = parse_result_dictionary(output, n_passed, n_failed, n_undetermined, message)

        writer.writerow([f"'{rule_id}",
                         output["standard_section"],
                         output["description"],
                         output["primary_rule"],
                         output["rule_evaluation_outcome"],
                         n_passed,
                         n_failed,
                         n_undetermined,
                         message])