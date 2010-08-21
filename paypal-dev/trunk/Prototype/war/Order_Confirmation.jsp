
<%
/*==================================================================
 PayPal Express Checkout Call
 ===================================================================
*/
String token = (String)session.getAttribute("token");
if ( token != null)
{
%>
<%@include file="Paypal_Functions.jsp"%>
<% 
	/*
	'------------------------------------
	' Get the token parameter value stored in the session 
	' from the previous SetExpressCheckout call
	'------------------------------------
	*/
	token =  (String)session.getAttribute("TOKEN");

	/*
	'------------------------------------
	' The paymentAmount is the total value of 
	' the shopping cart, that was set 
	' earlier in a session variable 
	' by the shopping cart page
	'------------------------------------
	*/
	
	String finalPaymentAmount =  (String)session.getAttribute("Payment_Amount");
	/*
	'------------------------------------
	' Calls the DoExpressCheckoutPayment API call
	'
	' The ConfirmPayment function is defined in the file PayPalFunctions.jsp,
	' that is included at the top of this file.
	'-------------------------------------------------
	*/

	HashMap nvp = ConfirmPayment ( session, request, finalPaymentAmount );
	String strAck = nvp.get("ACK").toString();
	if(strAck !=null && (strAck.equalsIgnoreCase("Success") || strAck.equalsIgnoreCase("SuccessWithWarning")))
	{
		/*
		'********************************************************************************************************************
		'
		' THE PARTNER SHOULD SAVE THE KEY TRANSACTION RELATED INFORMATION LIKE 
		'                    transactionId & orderTime 
		'  IN THEIR OWN  DATABASE
		' AND THE REST OF THE INFORMATION CAN BE USED TO UNDERSTAND THE STATUS OF THE PAYMENT 
		'
		'********************************************************************************************************************
		*/

		String transactionId	= getNonEmptyValue( nvp, "TRANSACTIONID" ); // ' Unique transaction ID of the payment. Note:  If the PaymentAction of the request was Authorization or Order, this value is your AuthorizationID for use with the Authorization & Capture APIs. 
		String transactionType 	= getNonEmptyValue( nvp, "TRANSACTIONTYPE" ); //' The type of transaction Possible values: l  cart l  express-checkout 
		String paymentType		= getNonEmptyValue( nvp, "PAYMENTTYPE" );  //' Indicates whether the payment is instant or delayed. Possible values: l  none l  echeck l  instant 
		String orderTime 		= getNonEmptyValue( nvp, "ORDERTIME" );  //' Time/date stamp of payment
		String amt				= getNonEmptyValue( nvp, "AMT" );  //' The final amount charged, including any shipping and taxes from your Merchant Profile.
		String currencyCode		= getNonEmptyValue( nvp, "CURRENCYCODE" );  //' A three-character currency code for one of the currencies listed in PayPay-Supported Transactional Currencies. Default: USD. 
		String feeAmt			= getNonEmptyValue( nvp, "FEEAMT" );  //' PayPal fee amount charged for the transaction
		String settleAmt		= getNonEmptyValue( nvp, "SETTLEAMT" );  //' Amount deposited in your PayPal account after a currency conversion.
		String taxAmt			= getNonEmptyValue( nvp, "TAXAMT" );  //' Tax charged on the transaction.
		String exchangeRate		= getNonEmptyValue( nvp, "EXCHANGERATE" );  //' Exchange rate if a currency conversion occurred. Relevant only if your are billing in their non-primary currency. If the customer chooses to pay with a currency other than the non-primary currency, the conversion occurs in the customer’s account.
		
		/*
		' Status of the payment: 
				'Completed: The payment has been completed, and the funds have been added successfully to your account balance.
				'Pending: The payment is pending. See the PendingReason element for more information. 
		*/
		
		String paymentStatus	= getNonEmptyValue( nvp, "PAYMENTSTATUS" ); 

		/*
		'The reason the payment is pending:
		'  none: No pending reason 
		'  address: The payment is pending because your customer did not include a confirmed shipping address and your Payment Receiving Preferences is set such that you want to manually accept or deny each of these payments. To change your preference, go to the Preferences section of your Profile. 
		'  echeck: The payment is pending because it was made by an eCheck that has not yet cleared. 
		'  intl: The payment is pending because you hold a non-U.S. account and do not have a withdrawal mechanism. You must manually accept or deny this payment from your Account Overview. 		
		'  multi-currency: You do not have a balance in the currency sent, and you do not have your Payment Receiving Preferences set to automatically convert and accept this payment. You must manually accept or deny this payment. 
		'  verify: The payment is pending because you are not yet verified. You must verify your account before you can accept this payment. 
		'  other: The payment is pending for a reason other than those listed above. For more information, contact PayPal customer service. 
		*/
		
		String pendingReason	= getNonEmptyValue( nvp, "PENDINGREASON" );  

		/*
		'The reason for a reversal if TransactionType is reversal:
		'  none: No reason code 
		'  chargeback: A reversal has occurred on this transaction due to a chargeback by your customer. 
		'  guarantee: A reversal has occurred on this transaction due to your customer triggering a money-back guarantee. 
		'  buyer-complaint: A reversal has occurred on this transaction due to a complaint about the transaction from your customer. 
		'  refund: A reversal has occurred on this transaction because you have given the customer a refund. 
		'  other: A reversal has occurred on this transaction due to a reason not listed above. 
		*/
		
		String reasonCode		= getNonEmptyValue( nvp, "REASONCODE" );
		%>
<h1>Order In Process...</h1>
Bold variables must be saved in our DB (according to PayPal agreement)
<table width="700" style="border: 1px solid black;">
	<tr>
		<td><b><%= transactionId %></b></td>
		<td>Unique transaction ID of the payment. Note: If the
		PaymentAction of the request was Authorization or Order, this value is
		your AuthorizationID for use with the Authorization & Capture APIs.</td>
	</tr>
	<tr>
		<td><%= transactionType %></td>
		<td>The type of transaction Possible values: l cart l
		express-checkout</td>
	</tr>
	<tr>
		<td><%= paymentType %></td>
		<td>Indicates whether the payment is instant or delayed. Possible
		values: l none l echeck l instant</td>
	</tr>
	<tr>
		<td><b><%= orderTime %></b></td>
		<td>Time/date stamp of payment</td>
	</tr>
	<tr>
		<td><%= amt %></td>
		<td>The final amount charged, including any shipping and taxes
		from your Merchant Profile.</td>
	</tr>
	<tr>
		<td><%= currencyCode %></td>
		<td>A three-character currency code for one of the currencies
		listed in PayPay-Supported Transactional Currencies. Default: USD.</td>
	</tr>
	<tr>
		<td><%= feeAmt %></td>
		<td>PayPal fee amount charged for the transaction</td>
	</tr>
	<tr>
		<td><%= settleAmt %></td>
		<td>Amount deposited in your PayPal account after a currency
		conversion.</td>
	</tr>
	<tr>
		<td><%= taxAmt %></td>
		<td>Tax charged on the transaction.</td>
	</tr>
	<tr>
		<td><%= exchangeRate %></td>
		<td>Exchange rate if a currency conversion occurred. Relevant
		only if your are billing in their non-primary currency. If the
		customer chooses to pay with a currency other than the non-primary
		currency, the conversion occurs in the customer's account.</td>
	</tr>
</table>
<%
	}
	else
	{  
		// Display a user friendly Error on the page using any of the following error information returned by PayPal
		
		String ErrorCode = getNonEmptyValue( nvp, "L_ERRORCODE0" );
		String ErrorShortMsg = getNonEmptyValue( nvp, "L_SHORTMESSAGE0" );
		String ErrorLongMsg = getNonEmptyValue( nvp, "L_LONGMESSAGE0" );
		String ErrorSeverityCode = getNonEmptyValue( nvp, "L_SEVERITYCODE0" );
		
		out.println( "Order Confirmation failed <br/>");
		out.println( "Detailed Error Message: " + ErrorLongMsg + "<br/>");
		out.println( "Short Error Message: " + ErrorShortMsg + "<br/>");
		out.println( "Error Code: " + ErrorCode + "<br/>");
		out.println( "Error Severity Code: " + ErrorSeverityCode + "<br/>");
	}
}		
		
%>