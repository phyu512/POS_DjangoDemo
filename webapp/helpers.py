from datetime import datetime

class DateUtils:
    @staticmethod
    def format_dd_mmm_yyyy(date_obj):
        """
        Converts a datetime or date object to string format: dd-MMM-yyyy
        Example: 22-Feb-2026
        """
        if not date_obj:
            return ""
        return date_obj.strftime("%d-%b-%Y")