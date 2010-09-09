package com.solvers.prototype.server;


import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.UUID;
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

import org.apache.catalina.HttpResponse;

import com.google.appengine.repackaged.com.google.common.base.StringUtil;
import com.google.appengine.repackaged.org.json.JSONException;
import com.google.appengine.repackaged.org.json.JSONObject;

public class TestService extends HttpServlet {
	public TestService() {
		super();
		
		myUsers = new HashMap<String, String>();		
		myUsers.put( "abd", "alexander.a.borodin@gmail.com" );
		myUsers.put( "apo", "alexey.petrov.nnov@gmail.com" );
		
		myServiceInstances = new ArrayList<UUID>();
	}

	/**
	 * serialVersionUID
	 */
	private static final long serialVersionUID = -1354799645706287792L;

	private static final Logger log = Logger.getLogger(TestService.class.getName());
	
	//users map
	private HashMap<String, String> myUsers;
	
	//list of requested services
	private List<UUID> myServiceInstances;

    public void doPost(HttpServletRequest req, HttpServletResponse resp)
                throws IOException
    {
    	String uid = req.getParameter("UID");
    	if ( StringUtil.isEmpty(uid) )
    	{
    		resp.getWriter().println( "Error: Invalid 'UID' parameter ");
    		log.log( Level.SEVERE, "Invalid 'UID' parameter " );
    		return;
    	}
    	String email = myUsers.get(uid);
    	if ( email == null )
    	{
    		String msg = String.format("Error: No registered user with such UID = %s", uid );
    		resp.getWriter().println( msg);
    		log.log( Level.WARNING, msg );
    		return;
    	}
    	
    	String method = req.getParameter("Method");
    	if( StringUtil.isEmpty(method) )
    	{
    		resp.getWriter().println( "Error: Invalid 'Method' parameter ");
    		log.log( Level.SEVERE, "Invalid 'Method' parameter " );
    		return;
    	}
    	
    	if( method.equalsIgnoreCase("GETService") )
    	{
    		String aServiceId = GetService();
    		resp.setStatus(HttpServletResponse.SC_OK);

    		resp.setContentType("text/x-json;charset=UTF-8");           
            resp.setHeader("Cache-Control", "no-cache");
            try {
            	JSONObject json = new JSONObject();
                json.put("ServiceId", aServiceId);
    	        json.write(resp.getWriter());
	    	} catch (IOException e) {
	    		log.log( Level.SEVERE, "IOException in writing JSON" );    	    
	    	} catch (JSONException e) {
	    		log.log( Level.SEVERE, "JSONException in creation JSON" );
			}

    	}
    	
    	
    	
    	
    	
    	/*    	
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
        
        try {
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
        //resp.getWriter().println("Notification e-mail was sent succesiful!");        
    }
    
    /*
     * This method is called when request GetService comes
     */
    private String GetService()
    {
    	//generate new UID for service instance
    	UUID aGenUID = UUID.randomUUID();
    	myServiceInstances.add(aGenUID);    	
    	return aGenUID.toString();    	    
    }
}