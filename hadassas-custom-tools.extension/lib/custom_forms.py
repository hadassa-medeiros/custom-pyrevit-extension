# -*- coding: utf-8 -*-
from pyrevit import forms
from pyrevit.forms import WPFWindow
import os

dir_path = os.path.dirname(__file__)
path_styles= os.path.join(dir_path, 'Resources/custom_form_styles.xaml')

class CustomInput(WPFWindow):
    def __init__(self, prompt_text):
        xaml_path = r'{}'.format(path_styles)
        super(CustomInput, self).__init__(xaml_path)
        self.PromptText.Text = prompt_text
        self.input_text = ""


    def OnConfirm(self, sender, args):
        self.input_text = self.InputBox.Text
        self.Close()

# class CustomInput(forms.WPFWindow):
#     def __init__(self):
#         # super(CustomInput, self).__init__("")
#         self.Title = "Digite os níveis"
#         self.Width = 600  # Ajuste conforme necessário
#         self.Height = 200
#         self.input_text = ""
    
#     def get_text_input(self, prompt, default):
#         self.input_text = forms.ask_for_string(
#             prompt=prompt,
#             default=default
#         )
#         self.Close()