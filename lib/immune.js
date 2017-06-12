'use strict';

/**
 * Add medical provider to child record
 * @param {ibm.wsc.immunichain.assignMedProvider} assignMedProvider - the assignMedProvider transaction
 * @transaction
 */
function assignMedProvider(assignMedProvider) {
 var gid = assignMedProvider.guardian.gid;
 var cid = assignMedProvider.childform.cid;
 var mid = assignMedProvider.medprovider.medid;
 assignMedProvider.childform.medproviders.push(mid);
 
 return getAssetRegistry('ibm.wsc.immunichain.Childform').then(function(result) {
            return result.update(assignMedProvider.childform);
        }
    );
}

/**
 * Authorize member to child record
 * @param {ibm.wsc.immunichain.authMember} authMember - the authMember transaction
 * @transaction
 */
function authMember(authMember) {
 var gid = authMember.guardian.gid;
 var cid = authMember.childform.cid;
 var mid = authMember.member.memid;
 authMember.childform.members.push(mid);
 
 return getAssetRegistry('ibm.wsc.immunichain.Childform').then(function(result) {
            return result.update(authMember.childform.members);
        }
    );
}

/**
 * Deauthorize member to child record, so remove from members list
 * @param {ibm.wsc.immunichain.removeMemberAuth} removeMemberAuth - the removeMemberAuth transaction
 * @transaction
 */
function removeMemberAuth(removeMemberAuth) {
	var gid = removeMemberAuth.guardian.gid;
	var cid = removeMemberAuth.childform.cid;
	var mid = removeMemberAuth.member.memid;
	var mem = removeMemberAuth.childform.members
	var idx = mem.indexOf(mid);

	//if the member is in the array of Members, we can remove it
	if (idx !== -1){
		removeMemberAuth.childform.members.splice(idx,1);
	}

	return getAssetRegistry('ibm.wsc.immunichain.Childform')
		.then(function(result) {
			return result.update(removeMemberAuth.childform.members);
        });
}

/**
 * Add immunization(s) to child record
 * @param {ibm.wsc.immunichain.addImmunizations} addImmunizations - the addImmunizations transaction
 * @transaction
 */
function addImmunizations(addImmunizations){
	var vaccines = addImmunizations.vaccines;
	var child = addImmunizations.childform;
	for (vaccine in vaccines){
		addImmunizations.childform.immunizations.push(vaccine)
	};
	return getAssetRegistry('ibm.wsc.immunichain.Childform')
		.then(function(ChildRegistry){
			//save the childform
			return ChildRegistry.update(addImmunizations.childform.immunizations);
		});
}

/**
 * Get the immunizations for a child
 * @query
 * @param {String} cid - the unique id assigned to the childform
 * @returns {immunirecord[]} - the immunizations that the child has gotten
*/
function listImmunizations(cid) {
  return query('select x.immunizations from Childform where x.cid ==: cid');
}

