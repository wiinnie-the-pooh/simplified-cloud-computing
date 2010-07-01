<%
	/*==================================================================
	 PayPal Express Checkout Call
	 ===================================================================
	*/
%>
<%@include file="Paypal_Functions.jsp" %>
<%
if (PaymentOption == "PayPal")
{
	/*
	'------------------------------------
	' The paymentAmount is the total value of 
	' the shopping cart, that was set 
	' earlier in a session variable 
	' by the shopping cart page
	'------------------------------------
	*/

	String paymentAmount = (String)session.getAttribute("Payment_Amount");

	/*
	'------------------------------------
	' The currencyCodeType and paymentType 
	' are set to the selections made on the Integration Assistant 
	'------------------------------------
	*/

	String currencyCodeType = "USD";
	String paymentType = "Sale";

	/*
	'------------------------------------
	' The returnURL is the location where buyers return to when a
	' payment has been succesfully authorized.
	'
	' This is set to the value entered on the Integration Assistant 
	'------------------------------------
	*/

	String returnURL = "http://localhost/return_url.php";

	/*
	'------------------------------------
	' The cancelURL is the location buyers are sent to when they hit the
	' cancel button during authorization of payment during the PayPal flow
	'
	' This is set to the value entered on the Integration Assistant 
	'------------------------------------
	*/
	String cancelURL = "http://localhost/cancel_url.php";

	/*
	'------------------------------------
	' When you integrate this code 
	' set the variables below with 
	' shipping address details 
	' entered by the user on the 
	' Shipping page.
	'------------------------------------
	*/

	String shipToName 			= "<<ShiptoName>>";
	String shipToStreet 		= "<<ShipToStreet>>";
	String shipToStreet2 		= "<<ShipToStreet2>>"; //'Leave it blank if there is no value
	String shipToCity 			= "<<ShipToCity>>";
	String shipToState 			= "<<ShipToState>>";
	String shipToCountryCode 	= "<<ShipToCountryCode>>"; //' Please refer to the PayPal country codes in the API documentation
	String shipToZip 			= "<<ShipToZip>>";
	String phoneNum 			= "<<PhoneNumber>>";

	/*
	'------------------------------------
	' Calls the SetExpressCheckout API call
	'
	' The CallMarkExpressCheckout function is defined in the file PayPalFunctions.asp,
	' it is included at the top of this file.
	'-------------------------------------------------
	*/

	HashMap nvp = CallMarkExpressCheckout (paymentAmount, currencyCodeType, paymentType, returnURL, cancelURL,
									shipToName, shipToStreet, shipToStreet2, shipToCity, shipToState,
									shipToCountryCode, shipToZip, phoneNum );
									
	String strAck = nvp.get("ACK").toString();
	if(strAck !=null && !(strAck.equalsIgnoreCase("Success") || strAck.equalsIgnoreCase("SuccessWithWarning")))
	{
		//' Redirect to paypal.com
		ReDirectURL( nvp.get("TOKEN").toString());
	}
	else
	{  
		// Display a user friendly Error on the page using any of the following error information returned by PayPal
		
		String ErrorCode = nvp.get("L_ERRORCODE0").toString();
		String ErrorShortMsg = nvp.get("L_SHORTMESSAGE0").toString();
		String ErrorLongMsg = nvp.get("L_LONGMESSAGE0").toString();
		String ErrorSeverityCode = nvp.get("L_SEVERITYCODE0").toString();
	}
}
else
{
 if (((PaymentOption == "Visa") || (PaymentOption == "MasterCard") || (PaymentOption == "Amex") || (PaymentOption = "Discover"))
			&& ( PaymentProcessorSelected == "PayPal Direct Payment")) {

	/*		
	'------------------------------------
	' The paymentAmount is the total value of 
	' the shopping cart, that was set 
	' earlier in a session variable 
	' by the shopping cart page
	'------------------------------------
	*/
	String paymentAmount = (String)session.getAttribute("Payment_Amount");

	/*
	'------------------------------------
	' The paymentType that was selected earlier 
	'------------------------------------
	*/
	String paymentType = "Sale";
	
	/*
	' Set these values based on what was selected by the user on the Billing page Html form
	*/
	
	String creditCardType 		= "<<Visa/MasterCard/Amex/Discover>>"; //' Set this to one of the acceptable values (Visa/MasterCard/Amex/Discover) match it to what was selected on your Billing page
	String creditCardNumber 	= "<<CC number>>"; // ' Set this to the string entered as the credit card number on the Billing page
	String expDate 				= "<<Expiry Date>>"; // ' Set this to the credit card expiry date entered on the Billing page
	String cvv2 				= "<<cvv2>>"; // ' Set this to the CVV2 string entered on the Billing page 
	String firstName 			= "<<firstName>>"; // ' Set this to the customer's first name that was entered on the Billing page 
	String lastName 			= "<<lastName>>"; // ' Set this to the customer's last name that was entered on the Billing page 
	String street 				= "<<street>>"; // ' Set this to the customer's street address that was entered on the Billing page 
	String city 				= "<<city>>"; // ' Set this to the customer's city that was entered on the Billing page 
	String state 				= "<<state>>"; // ' Set this to the customer's state that was entered on the Billing page 
	String zip 					= "<<zip>>"; // ' Set this to the zip code of the customer's address that was entered on the Billing page 
	String countryCode 			= "<<PayPal Country Code>>"; // ' Set this to the PayPal code for the Country of the customer's address that was entered on the Billing page 
	String currencyCode 		= "<<PayPal Currency Code>>"; // ' Set this to the PayPal code for the Currency used by the customer 
	
	/*	
	'------------------------------------------------
	' Calls the DoDirectPayment API call
	'
	' The DirectPayment function is defined in PayPalFunctions.jsp 
	' included at the top of this file.
	'-------------------------------------------------
	*/
	nvp = DirectPayment ( paymentType, paymentAmount, creditCardType, creditCardNumber,
							expDate, cvv2, firstName, lastName, street, city, state, zip, 
							countryCode, currencyCode ); 

	String strAck = nvp.get("ACK").toString();
	if(strAck ==null || strAck.equalsIgnoreCase("Success") || strAck.equalsIgnoreCase("SuccessWithWarning") )
	{
		// Display a user friendly Error on the page using any of the following error information returned by PayPal
		String ErrorCode = nvp.get("L_ERRORCODE0").toString();
		String ErrorShortMsg = nvp.get("L_SHORTMESSAGE0").toString();
		String ErrorLongMsg = nvp.get("L_LONGMESSAGE0").toString();
		String ErrorSeverityCode = nvp.get("L_SEVERITYCODE0").toString();
	}
}
%>