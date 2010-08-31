package com.solvers.prototype.server;


import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.AddressException;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;
import javax.servlet.http.*;

public class TestService extends HttpServlet {
	public TestService() {
		super();
		
		myUsers = new HashMap<String, String>();		
		myUsers.put( "abd", "alexander.a.borodin@gmail.com" );
		myUsers.put( "apo", "alexey.petrov.nnov@gmail.com" );
	}

	/**
	 * serialVersionUID
	 */
	private static final long serialVersionUID = -1354799645706287792L;

	private static final Logger log = Logger.getLogger(TestService.class.getName());
	
	private HashMap<String, String> myUsers;

    public void doPost(HttpServletRequest req, HttpServletResponse resp)
                throws IOException
    {
    	String uid = req.getParameter("UID");
    	if ( uid == null || uid.length() == 0 )
    	{
    		resp.getWriter().println( "Invalid 'UID' parameter ");
    		log.log( Level.WARNING, "Invalid 'UID' parameter " );
    		return;
    	}
    	String email = myUsers.get(uid);
    	if ( email == null )
    	{
    		String msg = String.format("No registered user with such UID = %s", uid );
    		resp.getWriter().println( msg);
    		log.log( Level.WARNING, msg );
    		return;
    	}
    	    	
    	Properties props = new Properties();
        Session session = Session.getDefaultInstance(props, null);
        String msgBody = "Request log:\n";
        Map<String,String[]> aParameters = req.getParameterMap();
        Set<String> aKeys = aParameters.keySet();
        Iterator<String> anIt = aKeys.iterator();
        while (anIt.hasNext())
        {
        	String aKey = anIt.next();
        	if ( aKey == null )
        		continue;
        	msgBody += aKey + ":\t\t";
        	String[] aValues = aParameters.get(aKey);
        	if (aValues != null)
        	{
        		msgBody += Arrays.toString(aValues);
        	}
        	msgBody += "\n";
        }
          
        resp.getWriter().print(msgBody);
        
        /*try {
            Message msg = new MimeMessage(session);
            msg.setFrom(new InternetAddress("alexander.a.borodin@gmail.com"));
            msg.addRecipient(Message.RecipientType.TO,
                             new InternetAddress(email));
            msg.setSubject("Cloud Computing Notification");
            msg.setText(msgBody);
            Transport.send(msg);

        } catch (AddressException e) {
        	resp.getWriter().print( e.getMessage() );
            // ...
        } catch (MessagingException e) {
        	resp.getWriter().print( e.getMessage() );
            // ...
        }*/
        resp.getWriter().println("Notification e-mail was sent succesiful!");
        
    }
}