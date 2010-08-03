package com.solvers.prototype.server;


import java.io.IOException;
import java.util.logging.Logger;
import javax.servlet.http.*;

public class ExpressCheckout extends HttpServlet {
	private static final Logger log = Logger.getLogger(ExpressCheckout.class.getName());

    public void doPost(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
    	resp.sendRedirect("/Expresscheckout.jsp");
    }

}
