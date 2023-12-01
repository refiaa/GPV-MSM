# JUST FOR TESTING NOTHING HERE

### in GPvMSM.py

 def download_files(self):
     dates = self._get_dates_in_range()
     with ThreadPoolExecutor(max_workers=5) as executor:
         futures = [executor.submit(self._download_file_for_date, date) for date in dates]
         for future in as_completed(futures):
             try:
                 future.result()
             except Exception as exc:
                 print(f'download Exception: {exc}')

wanna use it in futher change in better way 