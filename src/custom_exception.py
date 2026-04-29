import sys

class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        """
        :param error_message: error message in string format
        :param error_detail: the sys module, used to extract traceback
        """
        super().__init__(error_message)
        self.error_message = self.get_detailed_error_message(error_message, error_detail)

    @staticmethod
    def get_detailed_error_message(error_message, error_detail: sys):
        # sys.exc_info() returns (type, value, traceback)
        _, _, exc_tb = error_detail.exc_info()
        
        # If there is no active exception, provide a fallback
        if exc_tb is not None:
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
            return f"Error occurred in python script: [{file_name}] line number: [{line_number}] error message: [{error_message}]"
        
        return error_message
    
    def __str__(self):
        return self.error_message