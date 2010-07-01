<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>PayPal Prototype</title>
</head>
<body>
	<div style="text-align:center">
		<h1>Express Checkout</h1>
		<form action="Express_Checkout.jsp" method="POST">
			<input type="text" name="AMOUNT" value="10"/>
			<select name="CURRENCY">
				<option value="USD">American Dollars(USD)</option>
				<option value="EUR">Europian Euros(EUR)</option>
				<option value="RUR">Russian Rubles(RUR)</option>		
			</select>
			<br/>
			<input type="image" name="submit" src="https://www.paypal.com/en_US/i/btn/btn_xpressCheckout.gif" alt='Check out with PayPal'>
		</form>
	</div>
</body>
</html>