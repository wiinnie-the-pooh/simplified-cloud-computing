package com.solvers.prototype.server;

import com.solvers.prototype.client.PrototypeService;
//import com.solvers.prototype.shared.FieldVerifier;
import com.google.gwt.user.server.rpc.RemoteServiceServlet;

import java.util.Properties;
import javax.mail.internet.AddressException;
import javax.mail.internet.InternetAddress;
import javax.mail.MessagingException;
import javax.mail.internet.MimeMessage;
import javax.mail.Message;
import javax.mail.Session;
import javax.mail.Transport;

/**
 * The server side implementation of the RPC service.
 */
@SuppressWarnings("serial")
public class PrototypeServiceImpl extends RemoteServiceServlet implements
PrototypeService {

	public String prototypeServer(String input){
		Properties props = new Properties();
        Session session = Session.getDefaultInstance(props, null);
        String msgBody = "...";
        
        try {
            Message msg = new MimeMessage(session);
            msg.setFrom(new InternetAddress("alexander.a.borodin@gmail.com"));
            msg.addRecipient(Message.RecipientType.TO,
                             new InternetAddress("alexander.a.borodin@gmail.com"));
            msg.setSubject("Cloud Computing Notification");
            msg.setText(msgBody);
            Transport.send(msg);

        } catch (AddressException e) {
        	return e.getMessage();
            // ...
        } catch (MessagingException e) {
        	return e.getMessage();
            // ...
        }
        return "Notification e-mail was sent succesiful!";
	}
}
