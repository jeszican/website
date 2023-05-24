
import smtplib
from email.message import EmailMessage

class Email():

	def send_submission(self, team, challenge, upload):
		# save the temp file 
		# f = tempfile.TemporaryFile()
		# f.write()
		# send message to me
		msg = EmailMessage()
		msg.set_content("""You have recieved a new submission for your challenge '%s' from team '%s'.\n\nOnce you have marked the work please email the final scores to Nye Prior @ admin@dctf.live\n""" % (challenge.name, team.team_name))
		msg['Subject'] = 'DCTF New Challenge Submission'
		msg['From'] = "Deloitte CTF <jessicanatashamail@gmail.com>"
		msg['To'] = "%s" % challenge.email
		# add the attachment
		content = upload.read()
		msg.add_attachment(content, maintype='application/pdf', subtype='pdf', filename='%s_submission.pdf' % team.team_name)
		upload.close()
		# Send the message via our own SMTP server.
		s = smtplib.SMTP('smtp.gmail.com')
		s.starttls()
		s.login("jessicanatashamail@gmail.com","ntenznudunhxxduy")
		# send our message
		s.send_message(msg)
		s.quit()
