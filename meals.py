from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import dotenv_values


def setup_google_sheets_api():
    env_vars = dotenv_values()
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials), env_vars.get('GOOGLE_SHEETS_ID')


def get_data(service, spreadsheet_id, range_):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_).execute()
    return result.get('values', [])


def print_data(values):
    if not values:
        print('No data found.')
    else:
        for row in values:
            print(' || '.join(row))


def main():
    service, spreadsheet_id = setup_google_sheets_api()
    range_ = 'YEMEK!A1:F5000'
    values = get_data(service, spreadsheet_id, range_)
    print_data(values)


if __name__ == "__main__":
    main()
