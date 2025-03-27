import pandas as pd  

def run(path):     
    try:
        attendance_df = pd.read_excel(path, sheet_name="Attendance_data")
        student_df = pd.read_excel(path, sheet_name="Student_data")

        attendance_df["attendance_date"] = pd.to_datetime(attendance_df["attendance_date"])

        df_absent = attendance_df[attendance_df["status"] == "Absent"]
        
        df_absent["shift"] = df_absent.groupby("student_id")["attendance_date"].shift(1)
        df_absent["gap"] = (df_absent["attendance_date"] - df_absent["shift"]).dt.days
        df_absent["group"] = (df_absent["gap"] > 1).cumsum()

        absence_groups = df_absent.groupby(["student_id", "group"])["attendance_date"].agg(["min", "max", "count"]).reset_index()
        absence_groups.columns = ["student_id", "group", "absence_start_date", "absence_end_date", "total_absent_days"]


        merged_df = absence_groups.merge(student_df, on="student_id", how="left")

        merged_df["student_name"] = merged_df["student_name"].fillna("Unknown Student")
        merged_df["parent_email"] = merged_df["parent_email"].fillna("No Email Provided")


        merged_df["msg"] = merged_df.apply(lambda row: (
            f"{row['student_name']} (ID: {row['student_id']}) was absent from {row['absence_start_date'].date()} "
            f"to {row['absence_end_date'].date()} for {row['total_absent_days']} days. "
            f"Notification sent to {row['parent_email']}."
        ), axis=1)

        return merged_df[["student_id", "student_name", "absence_start_date", "absence_end_date", "total_absent_days", "parent_email", "msg"]]

    except Exception as e:
        print(f"Error: {e}")

file_path = r"data - sample.xlsx"

output_df = run(file_path)
print(output_df)
