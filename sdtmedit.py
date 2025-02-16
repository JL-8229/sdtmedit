import wx
import wx.richtext as rt
import re
import csv

# Set DEBUG mode
DEBUG = "Y"  # Change to "N" to disable debug messages.

def debug(message):
    """Simple debug function to print messages if DEBUG is enabled."""
    if DEBUG == "Y":
        print(message)

def load_words_from_csv(file_path):
    """Loads words from a CSV file and returns a set of words."""
    words = set()
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Assuming each row contains single words
                words.update(word.strip().upper() for word in row)
    except Exception as e:
        debug(f"Error reading {file_path}: {e}")
    return words

class HighlighterFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(HighlighterFrame, self).__init__(*args, **kw)

        # Load words from CSV files
        self.source_words = load_words_from_csv('source_list.csv')
        self.target_words = load_words_from_csv('target_list.csv')
        self.function_list = load_words_from_csv('function_list.csv')

        debug(f"Initialized with source_words: {self.source_words}, target_words: {self.target_words}, function_list: {self.function_list}")

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create RichTextCtrl
        self.rich_text = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.check_button = wx.Button(panel, label='Check Words')
        self.uppercase_button = wx.Button(panel, label='Uppercase')  # New Uppercase button

        vbox.Add(self.rich_text, 1, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.check_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        vbox.Add(self.uppercase_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Add Uppercase button to layout
        panel.SetSizer(vbox)

        # Bind events
        self.check_button.Bind(wx.EVT_BUTTON, self.highlight_words)
        self.uppercase_button.Bind(wx.EVT_BUTTON, self.convert_to_uppercase)  # Bind uppercase button
        self.rich_text.Bind(wx.EVT_TEXT, self.on_text_change)  # Hook to text change event

        self.SetTitle('Word Highlighter')
        self.SetSize((600, 400))
        self.Centre()

    def on_text_change(self, event):
        """Handle text change event to highlight words."""
        # Call highlight after any change in text
        self.highlight_words(event)

    def highlight_words(self, event):
        text = self.rich_text.GetValue()
        debug(f"Text entered: {text}")

        words = set(re.findall(r'\b\w+\b', text))
        debug(f"Unique words found: {words}")

        # Reset styles
        self.rich_text.SetStyle(0, len(text), wx.TextAttr(wx.BLACK))
        for word in words:
            color = wx.BLACK
            upper_word = word.upper()
            if upper_word in self.source_words:
                color = wx.GREEN
            elif upper_word in self.target_words:
                color = wx.Colour(255, 165, 0)  # ORANGE
            elif upper_word in self.function_list:
                color = wx.BLUE
            else:
                color = wx.RED

            debug(f"Highlighting word: '{word}' with color: {color}")

            for match in re.finditer(r'\b' + re.escape(word) + r'\b', text):
                self.rich_text.SetStyle(match.start(), match.end(), wx.TextAttr(color))

    def convert_to_uppercase(self, event):
        """Convert the text in the RichTextCtrl to uppercase."""
        current_text = self.rich_text.GetValue()
        self.rich_text.SetValue(current_text.upper())  # Set the text to uppercase
        self.highlight_words(event)  # Re-highlight the text after conversion

class HighlighterApp(wx.App):
    def OnInit(self):
        frame = HighlighterFrame(None)
        frame.Show()
        return True

if __name__ == '__main__':
    app = HighlighterApp()
    app.MainLoop()
