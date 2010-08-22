package com.solvers.prototype.client;

import com.google.gwt.user.client.rpc.AsyncCallback;

/**
 * The async counterpart of <code>PrototypeService</code>.
 */
public interface PrototypeServiceAsync {
	void prototypeServer(String input, AsyncCallback<String> callback)
			throws IllegalArgumentException;
}
