<%
	/*==================================================================
	 PayPal Express Checkout Call
	 ===================================================================
	*/
%>
<%@include file="Paypal_Functions.jsp" %>
<%	
	session.setAttribute("Payment_Amount", request.getParameter("AMOUNT"));
	session.setAttribute("Payment_Currency", request.getParameter("CURRENCY"));
	
	String serverName = (String)request.getServerName();
	serverName += ":" + request.getServerPort();

	/*
	'-------------------------------------------
	' The paymentAmount is the total value of 
	' the shopping cart, that was set 
	' earlier in a session variable 
	' by the shopping cart page
	'-------------------------------------------
	*/

	String paymentAmount = (String) session.getAttribute("Payment_Amount");

	/*
	'------------------------------------
	' The currencyCodeType and paymentType 
	' are set to the selections made on the Integration Assistant 
	'------------------------------------
	*/

	String currencyCodeType = (String) session.getAttribute("Payment_Currency");;
	String paymentType = "Sale";

	/*
	'------------------------------------
	' The returnURL is the location where buyers return to when a
	' payment has been succesfully authorized.
	'
	' This is set to the value entered on the Integration Assistant 
	'------------------------------------
	*/

	String returnURL = "http://"+ serverName + "/Order_Review.jsp";

	/*
	'------------------------------------
	' The cancelURL is the location buyers are sent to when they hit the
	' cancel button during authorization of payment during the PayPal flow
	'
	' This is set to the value entered on the Integration Assistant 
	'------------------------------------
	*/
	String cancelURL = "http://"+ serverName + "/Main.jsp";

	/*
	'------------------------------------
	' Calls the SetExpressCheckout API call
	'
	' The CallShortcutExpressCheckout function is defined in the file PayPalFunctions.asp,
	' it is included at the top of this file.
	'-------------------------------------------------
	*/

	HashMap nvp = CallShortcutExpressCheckout (session, paymentAmount, currencyCodeType, paymentType, returnURL, cancelURL);
	String strAck = nvp.get("ACK").toString();
	if(strAck !=null && strAck.equalsIgnoreCase("Success"))
	{
		System.out.println( "Redirect to paypal.com...");
		System.out.println( "Server Name: " + serverName );
		//' Redirect to paypal.com
		RedirectURL( response, nvp.get("TOKEN").toString());
	}
	else
	{  
		// Display a user friendly Error on the page using any of the following error information returned by PayPal
		
		String ErrorCode = nvp.get("L_ERRORCODE0").toString();
		String ErrorShortMsg = nvp.get("L_SHORTMESSAGE0").toString();
		String ErrorLongMsg = nvp.get("L_LONGMESSAGE0").toString();
		String ErrorSeverityCode = nvp.get("L_SEVERITYCODE0").toString();
		
		out.println( "SetExpressCheckout API call failed <br/>");
		out.println( "Detailed Error Message: " + ErrorLongMsg + "<br/>");
		out.println( "Short Error Message: " + ErrorShortMsg + "<br/>");
		out.println( "Error Code: " + ErrorCode + "<br/>");
		out.println( "Error Severity Code: " + ErrorSeverityCode + "<br/>");
	}
%>
