from django.shortcuts import render
from django.shortcuts import redirect
from sqlmanager.views import *
from django.http import HttpResponseForbidden, HttpResponse
import logging

import smtplib
import ssl
from email.message import EmailMessage
import time

logger = logging.getLogger(__name__)

def adminDashboard(request):
    try:
        isAdmin = request.session.get("isAdmin")
        
        if not isAdmin:
            return HttpResponseForbidden("Admins only")

        company = request.session.get("company")
        
        if not company:
            logger.warning(f"Admin dashboard access without company information")
            return HttpResponse("Company information not found", status=400)

        try:
            rows = getEmployees(company)
            employees = []

            for row in rows:
                employee = {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "module1score": row[3],
                    "module2score": row[4]
                }
                employees.append(employee)
                
        except Exception as e:
            logger.error(f"Error fetching employees for company {company}: {str(e)}")
            employees = []

        return render(request, 'adminDashboard/adminDashboard.html', {"employees": employees, "company": company})
    except Exception as e:
        logger.error(f"Error in adminDashboard view: {str(e)}")
        return HttpResponse("An error occurred while loading the admin dashboard", status=500)

def sendEmail(request):
    try:
        company = request.session.get("company")

        if not company:
            return HttpResponse("Company not found in session", status=400)

        rows = getEmployees(company)

        if not rows:
            logger.warning(f"No employees found for company {company}")
            return HttpResponse("No employees found", status=404)

        subject = "Security Awareness Training"
        sender = "phishmedevelopment@gmail.com"
        password = "wbkz tlhu wqzg ekxq"

        context = ssl.create_default_context()

        success_count = 0
        failed_emails = []

        try:
            # Open ONE smtp connection for all emails
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(sender, password)

                # Loop through all employees
                for row in rows:
                    try:
                        employee_name = row[1]
                        employee_email = row[2]

                        body = f"""
Hello {employee_name},

This is a simulated phishing/security awareness email. Please follow the instructions found here: https://tinyurl.com/43tf9yyn

Time sent: {time.ctime()}

- Security Team
"""

                        em = EmailMessage()
                        em['From'] = sender
                        em['To'] = employee_email
                        em['Subject'] = subject
                        em.set_content(body)

                        smtp.send_message(em)

                        logger.info(f"Email sent successfully to {employee_email}")
                        success_count += 1

                    except Exception as e:
                        logger.error(f"Failed to send email to {employee_email}: {str(e)}")
                        failed_emails.append(employee_email)

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return HttpResponse("Email authentication failed", status=500)

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return HttpResponse("SMTP error occurred", status=500)
        
        htmlContent = "<br>".join([f"{email}: Failed to send" for email in failed_emails])
        htmlContent += f"<br>Emails sent successfully: {success_count}"
        htmlContent += "<br><button type='button' onclick=\"window.location.href='{% url 'adminDashboard:goToAdminDashboard' %}'\">Back to Dashboard</button>"
        return HttpResponse(htmlContent)

    except Exception as e:
        logger.error(f"Unexpected error in sendEmail: {str(e)}")
        return HttpResponse("An unexpected error occurred", status=500)

def goToDashboard(request):
    return redirect('dashboard:dashboard')

def goToAdminDashboard(request):
    return redirect('adminDashboard:adminDashboard')

def goToLeaderboard(request):
    return redirect('leaderboard:leaderboard')
   
def goToModules(request):
    return redirect('trainingModules:trainingModules')
    
def goToAchievements(request):
    return redirect('achievements:achievements')