import wx
import wx.richtext as rt
import re
import csv
import os  # For file dialogs

# Set DEBUG mode
DEBUG = "Y"  # Change to "N" to disable debug messages.

def debug(message):
    """Simple debug function to print messages if DEBUG is enabled."""
    if DEBUG == "Y":
        print(message)

def load_words_from_csv(file_path):
    """Loads words from a CSV file and returns a list of words."""
    words = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Assuming each row contains single words
                words.extend(word.strip().upper() for word in row)
    except Exception as e:
        debug(f"Error reading {file_path}: {e}")
    return words

class HighlighterFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(HighlighterFrame, self).__init__(*args, **kw)

        # Load words from CSV files
        self.source_words = load_words_from_csv('source_list.csv')
        self.target_words = load_words_from_csv('target_list.csv')
        self.function_list = sorted(load_words_from_csv('function_list.csv'))

        debug(f"Initialized with source_words: {self.source_words}, target_words: {self.target_words}, function_list: {self.function_list}")

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox_main = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox_left = wx.BoxSizer(wx.VERTICAL)
        vbox_center = wx.BoxSizer(wx.VERTICAL)
        vbox_right = wx.BoxSizer(wx.VERTICAL)

        # Create a read-only text box at the top
        self.top_text = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_CENTER)
        self.top_text.SetValue("SourceDomain=AE, TARGETDOMAIN=AE, MAPPINGVERSION=MK6552-003_3.4V1")

        # Create RichTextCtrl for source, target, and function words
        self.source_text = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.TE_READONLY)
        self.function_text = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.TE_READONLY)
        self.target_text = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.TE_READONLY)

        # Populate text boxes with words
        self.source_text.SetValue('\n'.join(self.source_words))
        self.function_text.SetValue('\n'.join(self.function_list))
        self.target_text.SetValue('\n'.join(self.target_words))

        # Create RichTextCtrl for the main editor
        self.rich_text = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.check_button = wx.Button(panel, label='Check Words')
        self.uppercase_button = wx.Button(panel, label='Uppercase')  # New Uppercase button
        self.load_button = wx.Button(panel, label='Load')  # New Load button
        self.save_button = wx.Button(panel, label='Save')  # New Save button
        self.copy_button = wx.Button(panel, label='Copy/Word')  # New Copy/Word button

        vbox_center.Add(self.rich_text, 1, wx.EXPAND | wx.ALL, 5)
        vbox_center.Add(self.check_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        vbox_center.Add(self.uppercase_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Add Uppercase button to layout
        vbox_center.Add(self.load_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Add Load button to layout
        vbox_center.Add(self.save_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Add Save button to layout
        vbox_center.Add(self.copy_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Add Copy/Word button to layout

        vbox_left.Add(self.source_text, 1, wx.EXPAND | wx.ALL, 5)
        vbox_right.Add(self.function_text, 1, wx.EXPAND | wx.ALL, 5)
        vbox_right.Add(self.target_text, 1, wx.EXPAND | wx.ALL, 5)

        hbox.Add(vbox_left, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(vbox_center, 3, wx.EXPAND | wx.ALL, 5)
        hbox.Add(vbox_right, 1, wx.EXPAND | wx.ALL, 5)

        vbox_main.Add(self.top_text, 0, wx.EXPAND | wx.ALL, 5)
        vbox_main.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox_main)

        # Bind events
        self.check_button.Bind(wx.EVT_BUTTON, self.highlight_words)
        self.uppercase_button.Bind(wx.EVT_BUTTON, self.convert_to_uppercase)  # Bind uppercase button
        self.load_button.Bind(wx.EVT_BUTTON, self.load_text)  # Bind load button
        self.save_button.Bind(wx.EVT_BUTTON, self.save_text)  # Bind save button
        self.copy_button.Bind(wx.EVT_BUTTON, self.copy_word_to_editor)  # Bind copy button
        self.rich_text.Bind(wx.EVT_TEXT, self.on_text_change)  # Hook to text change event

        # Bind double-click events
        self.source_text.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)
        self.function_text.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)
        self.target_text.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)

        self.SetTitle('Word Highlighter')
        self.SetSize((800, 600))
        self.Centre()

    def on_double_click(self, event):
        """Handle double-click event to add the selected word to the main editor."""
        obj = event.GetEventObject()
        if isinstance(obj, rt.RichTextCtrl):
            word = obj.GetStringSelection()
            if word:
                current_text = self.rich_text.GetValue()
                self.rich_text.SetValue(current_text + ' ' + word)
                debug(f"Added word '{word}' to the main editor.")
        event.Skip()

    def copy_word_to_editor(self, event):
        """Handle copy button click to add the selected word to the main editor."""
        selected_word = None
        for text_ctrl in [self.source_text, self.function_text, self.target_text]:
            word = text_ctrl.GetStringSelection()
            if word:
                selected_word = word
                break

        if selected_word:
            current_text = self.rich_text.GetValue()
            self.rich_text.SetValue(current_text + ' ' + selected_word)
            debug(f"Copied word '{selected_word}' to the main editor.")

    def on_text_change(self, event):
        """Handle text change event to highlight words."""
        # Call highlight after any change in text
        self.highlight_words(event)

    def highlight_words(self, event):
        text = self.rich_text.GetValue()
        debug(f"Text entered: {text}")

        # Remove text between quotes for checking
        text_to_check = re.sub(r'".*?"', '', text)

        lines = text_to_check.split('\n')
        self.rich_text.SetStyle(0, len(text), wx.TextAttr(wx.BLACK))

        # Create sets to track highlighted words
        highlighted_source_words = set()
        highlighted_function_words = set()
        highlighted_target_words = set()

        for line in lines:
            words = re.findall(r'\b\w+\b', line)
            if not words:
                continue

            for word in words:
                upper_word = word.upper()
                if upper_word in self.source_words:
                    color = wx.GREEN
                    highlighted_source_words.add(upper_word)
                elif upper_word in self.target_words:
                    color = wx.Colour(255, 165, 0)  # ORANGE
                    highlighted_target_words.add(upper_word)
                elif upper_word in self.function_list:
                    color = wx.BLUE
                    highlighted_function_words.add(upper_word)
                else:
                    color = wx.RED

                debug(f"Highlighting word: '{word}' with color: {color}")

                for match in re.finditer(r'\b' + re.escape(word) + r'\b', text):
                    self.rich_text.SetStyle(match.start(), match.end(), wx.TextAttr(color))

        # Function to highlight words in the text boxes
        def highlight_text_ctrl(text_ctrl, words, highlighted_words, color):
            text_ctrl.SetStyle(0, text_ctrl.GetLastPosition(), wx.TextAttr(wx.BLACK))
            for word in words:
                if word in highlighted_words:
                    for match in re.finditer(r'\b' + re.escape(word) + r'\b', text_ctrl.GetValue()):
                        text_ctrl.SetStyle(match.start(), match.end(), wx.TextAttr(color))

        # Highlight words in the text boxes
        highlight_text_ctrl(self.source_text, self.source_words, highlighted_source_words, wx.GREEN)
        highlight_text_ctrl(self.function_text, self.function_list, highlighted_function_words, wx.BLUE)
        highlight_text_ctrl(self.target_text, self.target_words, highlighted_target_words, wx.Colour(255, 165, 0))

    def convert_to_uppercase(self, event):
        """Convert the text in the RichTextCtrl to uppercase."""
        current_text = self.rich_text.GetValue()
        self.rich_text.SetValue(current_text.upper())  # Set the text to uppercase
        self.highlight_words(event)  # Re-highlight the text after conversion

    def load_text(self, event):
        """Load text from a file into the RichTextCtrl."""
        with wx.FileDialog(self, "Open text file", wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # The user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r', encoding='utf-8') as file:
                    self.rich_text.SetValue(file.read())
                self.highlight_words(event)  # Re-highlight the text after loading
                debug(f"Loaded text from {pathname}")
            except IOError as e:
                wx.LogError(f"Cannot open file '{pathname}': {e}")

    def save_text(self, event):
        """Save text from the RichTextCtrl to a file."""
        with wx.FileDialog(self, "Save text file", wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # The user changed their mind

            # Proceed saving the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w', encoding='utf-8') as file:
                    file.write(self.rich_text.GetValue())
                debug(f"Saved text to {pathname}")
            except IOError as e:
                wx.LogError(f"Cannot save current contents in file '{pathname}': {e}")

class HighlighterApp(wx.App):
    def OnInit(self):
        frame = HighlighterFrame(None)
        frame.Show()
        return True

if __name__ == '__main__':
    app = HighlighterApp()
    app.MainLoop()
