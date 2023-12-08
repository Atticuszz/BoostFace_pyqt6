# coding=utf-8
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PasswordLineEdit


class AuthDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget.setMinimumWidth(350)
        self.titleLabel = SubtitleLabel('Log in', self)

        # account line edit
        self.email_line_edit = LineEdit(self)
        self.email_line_edit.setPlaceholderText('Enter your account id')
        self.email_line_edit.setClearButtonEnabled(True)

        # password line edit
        self.password_line_edit = PasswordLineEdit(self)
        self.password_line_edit.setPlaceholderText(
            self.tr("Enter you password"))

        # button
        # check the password format and verify in the cloud
        self.yesButton.setText('Login')
        self.cancelButton.setText('Cancel')

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.email_line_edit)
        self.viewLayout.addWidget(self.password_line_edit)

        # self.account_line_edit.textChanged.connect(self._validateUrl)

    # def _validateUrl(self, text):
    #     self.yesButton.setEnabled(QUrl(text).isValid())
