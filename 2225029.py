import pandas as pd  

def process_attendance(file_path):     
    try:
        attendance_data = pd.read_excel(file_path, sheet_name="Attendance_data")
        student_info = pd.read_excel(file_path, sheet_name="Student_data")

        attendance_data["attendance_date"] = pd.to_datetime(attendance_data["attendance_date"])

        absent_records = attendance_data[attendance_data["status"] == "Absent"]

        absent_records["previous_date"] = absent_records.groupby("student_id")["attendance_date"].shift(1)
        absent_records["gap_days"] = (absent_records["attendance_date"] - absent_records["previous_date"]).dt.days
        absent_records["absence_group"] = (absent_records["gap_days"] > 1).cumsum()

        absence_summary = absent_records.groupby(["student_id", "absence_group"])["attendance_date"].agg(["min", "max", "count"]).reset_index()
        absence_summary.columns = ["student_id", "absence_group", "start_date", "end_date", "days_missed"]

        final_report = absence_summary.merge(student_info, on="student_id", how="left")

        final_report["student_name"].fillna("Unknown", inplace=True)
        final_report["parent_email"].fillna("No Email Provided", inplace=True)

        final_report["notification"] = final_report.apply(lambda row: (
            f"Student: {row['student_name']} (ID: {row['student_id']}) was absent from {row['start_date'].date()} "
            f"to {row['end_date'].date()} ({row['days_missed']} days). "
            f"Alert sent to {row['parent_email']}."
        ), axis=1)

        return final_report[["student_id", "student_name", "start_date", "end_date", "days_missed", "parent_email", "notification"]]

    except Exception as error:
        print(f"An error occurred while processing the file: {error}")

data_file = r"data - sample.xlsx"

result_df = process_attendance(data_file)
print(result_df)
