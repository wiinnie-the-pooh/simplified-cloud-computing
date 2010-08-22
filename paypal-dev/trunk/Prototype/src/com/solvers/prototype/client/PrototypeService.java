package com.solvers.prototype.client;

import com.google.gwt.user.client.rpc.RemoteService;
import com.google.gwt.user.client.rpc.RemoteServiceRelativePath;

/**
 * The client side stub for the RPC service.
 */
@RemoteServiceRelativePath("proto")
public interface PrototypeService extends RemoteService {
	String prototypeServer(String name) throws IllegalArgumentException;
}
