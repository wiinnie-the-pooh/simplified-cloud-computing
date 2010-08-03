<%
/*==================================================================
 PayPal Express Checkout Call
 ===================================================================
*/
String token = session.getAttribute("token");
if ( token != null)
{
%>
<%@include file="paypalfunctions.jsp" %>
<% 
	/*
	'------------------------------------
	' Get the token parameter value stored in the session 
	' from the previous SetExpressCheckout call
	'------------------------------------
	*/
	String token =  session.getAttribute("TOKEN");

	/*
	'------------------------------------
	' The paymentAmount is the total value of 
	' the shopping cart, that was set 
	' earlier in a session variable 
	' by the shopping cart page
	'------------------------------------
	*/
	
	String finalPaymentAmount =  session.getAttribute("Payment_Amount");
	/*
	'------------------------------------
	' Calls the DoExpressCheckoutPayment API call
	'
	' The ConfirmPayment function is defined in the file PayPalFunctions.jsp,
	' that is included at the top of this file.
	'-------------------------------------------------
	*/

	HashMap nvp = ConfirmPayment ( finalPaymentAmount );
	String strAck = nvp.get("ACK").toString();
	if(strAck !=null && !(strAck.equalsIgnoreCase("Success") || strAck.equalsIgnoreCase("SuccessWithWarning")))
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

		String transactionId	= nvp.get("TRANSACTIONID").toString(); // ' Unique transaction ID of the payment. Note:  If the PaymentAction of the request was Authorization or Order, this value is your AuthorizationID for use with the Authorization & Capture APIs. 
		String transactionType 	= nvp.get("TRANSACTIONTYPE").toString(); //' The type of transaction Possible values: l  cart l  express-checkout 
		String paymentType		= nvp.get("PAYMENTTYPE").toString();  //' Indicates whether the payment is instant or delayed. Possible values: l  none l  echeck l  instant 
		String orderTime 		= nvp.get("ORDERTIME").toString();  //' Time/date stamp of payment
		String amt				= nvp.get("AMT").toString();  //' The final amount charged, including any shipping and taxes from your Merchant Profile.
		String currencyCode		= nvp.get("CURRENCYCODE").toString();  //' A three-character currency code for one of the currencies listed in PayPay-Supported Transactional Currencies. Default: USD. 
		String feeAmt			= nvp.get("FEEAMT").toString();  //' PayPal fee amount charged for the transaction
		String settleAmt		= nvp.get("SETTLEAMT").toString();  //' Amount deposited in your PayPal account after a currency conversion.
		String taxAmt			= nvp.get("TAXAMT").toString();  //' Tax charged on the transaction.
		String exchangeRate		= nvp.get("EXCHANGERATE").toString();  //' Exchange rate if a currency conversion occurred. Relevant only if your are billing in their non-primary currency. If the customer chooses to pay with a currency other than the non-primary currency, the conversion occurs in the customer’s account.
		
		/*
		' Status of the payment: 
				'Completed: The payment has been completed, and the funds have been added successfully to your account balance.
				'Pending: The payment is pending. See the PendingReason element for more information. 
		*/
		
		String paymentStatus	= nvp.get("PAYMENTSTATUS").toString(); 

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
		
		String pendingReason	= nvp.get("PENDINGREASON").toString();  

		/*
		'The reason for a reversal if TransactionType is reversal:
		'  none: No reason code 
		'  chargeback: A reversal has occurred on this transaction due to a chargeback by your customer. 
		'  guarantee: A reversal has occurred on this transaction due to your customer triggering a money-back guarantee. 
		'  buyer-complaint: A reversal has occurred on this transaction due to a complaint about the transaction from your customer. 
		'  refund: A reversal has occurred on this transaction because you have given the customer a refund. 
		'  other: A reversal has occurred on this transaction due to a reason not listed above. 
		*/
		
		String reasonCode		= nvp.get("REASONCODE").toString();   
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
		
%>