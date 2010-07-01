<%
	/*==================================================================
	 PayPal Express Checkout Call
	 ===================================================================
	*/
/* 
	This step indicates whether the user was sent here by PayPal 
	if this value is null then it is part of the regular checkout flow in the cart
*/

String token = (String)request.getParameter("token");
if ( token != null)
{
%>
<%@include file="Paypal_Functions.jsp" %>
<%
	/*
	'------------------------------------
	' Calls the GetExpressCheckoutDetails API call
	'
	' The GetShippingDetails function is defined in PayPalFunctions.jsp
	' included at the top of this file.
	'-------------------------------------------------
	*/
	
	HashMap nvp = GetShippingDetails( session, token );
	String strAck = nvp.get("ACK").toString();
	if(strAck != null && !(strAck.equalsIgnoreCase("Success") || strAck.equalsIgnoreCase("SuccessWithWarning")))
	{
		String email 			= nvp.get("EMAIL").toString(); // ' Email address of payer.
		String payerId 			= nvp.get("PAYERID").toString(); // ' Unique PayPal customer account identification number.
		String payerStatus		= nvp.get("PAYERSTATUS").toString(); // ' Status of payer. Character length and limitations: 10 single-byte alphabetic characters.
		String salutation		= nvp.get("SALUTATION").toString(); // ' Payer's salutation.
		String firstName		= nvp.get("FIRSTNAME").toString(); // ' Payer's first name.
		String middleName		= nvp.get("MIDDLENAME").toString(); // ' Payer's middle name.
		String lastName			= nvp.get("LASTNAME").toString(); // ' Payer's last name.
		String suffix			= nvp.get("SUFFIX").toString(); // ' Payer's suffix.
		String cntryCode		= nvp.get("COUNTRYCODE").toString(); // ' Payer's country of residence in the form of ISO standard 3166 two-character country codes.
		String business			= nvp.get("BUSINESS").toString(); // ' Payer's business name.
		String shipToName		= nvp.get("SHIPTONAME").toString(); // ' Person's name associated with this address.
		String shipToStreet		= nvp.get("SHIPTOSTREET").toString(); // ' First street address.
		String shipToStreet2	= nvp.get("SHIPTOSTREET2").toString(); // ' Second street address.
		String shipToCity		= nvp.get("SHIPTOCITY").toString(); // ' Name of city.
		String shipToState		= nvp.get("SHIPTOSTATE").toString(); // ' State or province
		String shipToCntryCode	= nvp.get("SHIPTOCOUNTRYCODE").toString(); // ' Country code. 
		String shipToZip		= nvp.get("SHIPTOZIP").toString(); // ' U.S. Zip code or other country-specific postal code.
		String addressStatus 	= nvp.get("ADDRESSSTATUS").toString(); // ' Status of street address on file with PayPal   
		String invoiceNumber	= nvp.get("INVNUM").toString(); // ' Your own invoice or tracking number, as set by you in the element of the same name in SetExpressCheckout request .
		String phonNumber		= nvp.get("PHONENUM").toString(); // ' Payer's contact telephone number. Note:  PayPal returns a contact telephone number only if your Merchant account profile settings require that the buyer enter one. 

		/*
		' The information that is returned by the GetExpressCheckoutDetails call should be integrated by the partner into his Order Review 
		' page		
		*/
		out.println( "All is OK<br/>");
		%>
		<h1>Order Review</h1>
		<table width="700" style="border: 1px solid black;">	
			<tr><td><%= email %></td><td>Email address of payer.</td></tr>
			<tr><td><%= payerId %></td><td>Unique PayPal customer account identification number.</td></tr>
			<tr><td><%= payerStatus %></td><td>Status of payer. Character length and limitations: 10 single-byte alphabetic characters.</td></tr>
			<tr><td><%= salutation %></td><td>Payer's salutation.</td></tr>
			<tr><td><%= firstName %></td><td>Payer's first name.</td></tr>
			<tr><td><%= middleName %></td><td>Payer's middle name.</td></tr>
			<tr><td><%= lastName %></td><td>Payer's last name.</td></tr>
			<tr><td><%= suffix %></td><td>Payer's suffix.</td></tr>
			<tr><td><%= cntryCode %></td><td>Payer's country of residence in the form of ISO standard 3166 two-character country codes.</td></tr>
			<tr><td><%= business %></td><td>Payer's business name.</td></tr>
			<tr><td><%= shipToName %></td><td>Person's name associated with this address.</td></tr>
			<tr><td><%= shipToStreet %></td><td>First street address.</td></tr>
			<tr><td><%= shipToStreet2 %></td><td>Second street address.</td></tr>
			<tr><td><%= shipToCity %></td><td>Name of city.</td></tr>
			<tr><td><%= shipToState %></td><td>State or province</td></tr>
			<tr><td><%= shipToCntryCode %></td><td>Country code.</td></tr>
			<tr><td><%= shipToZip %></td><td>U.S. Zip code or other country-specific postal code.</td></tr>
			<tr><td><%= addressStatus %></td><td>Status of street address on file with PayPal</td></tr>
			<tr><td><%= invoiceNumber %></td><td>Your own invoice or tracking number, as set by you in the element of the same name in SetExpressCheckout request .</td></tr>
			<tr><td><%= phonNumber %></td><td>Payer's contact telephone number. Note:  PayPal returns a contact telephone number only if your Merchant account profile settings require that the buyer enter one. </td></tr>
		</table>
		<%
	}
	else
	{  
		// Display a user friendly Error on the page using any of the following error information returned by PayPal
		
		String ErrorCode = nvp.get("L_ERRORCODE0").toString();
		String ErrorShortMsg = nvp.get("L_SHORTMESSAGE0").toString();
		String ErrorLongMsg = nvp.get("L_LONGMESSAGE0").toString();
		String ErrorSeverityCode = nvp.get("L_SEVERITYCODE0").toString();
		
		out.println( "Get Billing Information failed <br/>");
		out.println( "Detailed Error Message: " + ErrorLongMsg + "<br/>");
		out.println( "Short Error Message: " + ErrorShortMsg + "<br/>");
		out.println( "Error Code: " + ErrorCode + "<br/>");
		out.println( "Error Severity Code: " + ErrorSeverityCode + "<br/>");
	}
}
%>



<form action='Order_Confirmation.jsp' METHOD='POST'>
	<input type='submit' value="Confirm Payment"/>
</form>