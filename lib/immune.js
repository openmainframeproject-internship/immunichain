'use strict';

/**
 * Add medical provider to child record
 * @param {ibm.wsc.immunichain.assignMedProvider} assignMedProvider - the assignMedProvider transaction
 * @transaction
 */
function assignMedProvider(assignMedProvider) {
  var guardian = assignMedProvider.guardian;
  var child = assignMedProvider.childform;
  var medprovider = assignMedProvider.medprovider;
  child.medproviders.push(medprovider);
  
  return getAssetRegistry('ibm.wsc.immunichain.Childform')
    .then(function(result) {
    	return result.update(child);
  	});
}

/**
 * Authorize member to child record
 * @param {ibm.wsc.immunichain.authMember} authMember - the authMember transaction
 * @transaction
 */
function authMember(authMember) {
  var guardian = authMember.guardian;
  var child = authMember.childform;
  var member = authMember.member;
  child.members.push(member);
  return getAssetRegistry('ibm.wsc.immunichain.Childform')
    .then(function(ChildRegistry) {
    	return ChildRegistry.update(child);
  	});
}

/**
 * Deauthorize member to child record, so remove from members list
 * @param {ibm.wsc.immunichain.removeMemberAuth} removeMemberAuth - the removeMemberAuth transaction
 * @transaction
 */
function removeMemberAuth(removeMemberAuth) {
	var guardian = removeMemberAuth.guardian;
	var child = removeMemberAuth.childform;
	var member = removeMemberAuth.member;
	var mem = child.members;
	var idx = mem.indexOf(member);

	//if the member is in the array of Members, we can remove it
	if (idx !== -1){
		mem.splice(idx,1);
	}

	return getAssetRegistry('ibm.wsc.immunichain.Childform')
		.then(function(result) {
			return result.update(child);
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
  	var immunizations = child.immunizations;
  	if (immunizations[0].name == 'default'){
    	immunizations.splice(0,1)
    }
  	immunizations.push.apply(immunizations,vaccines);
  
	return getAssetRegistry('ibm.wsc.immunichain.Childform')
		.then(function(ChildRegistry){
			//save the childform
			return ChildRegistry.update(child);
		});
}

/**
 * Update information on child record, can only be done by guardian
 * @param {ibm.wsc.immunichain.updateChildForm} updateChildForm - the updateChildForm transaction
 * @transaction
 */
function updateChildForm(updateChildForm){
  	var newaddress = null;
  	var newname = null;
    var child = updateChildForm.childform;
  	newaddress = updateChildForm.address;
  	newname = updateChildForm.name;
  
  	if (newaddress != null && newname != null){
    	child.name = newname;
      	child.address = newaddress;
    }
  	else if (newaddress != null){
    	child.address = newaddress;
    }
 	else if (newname != null){
    	child.name = newname;
    }
	return getAssetRegistry('ibm.wsc.immunichain.Childform')
		.then(function(ChildRegistry){
			//save the childform
			return ChildRegistry.update(child);
		});
}

/**
 * Assign child to his/herself when he/she is of legal age
 * @param {ibm.wsc.immunichain.reassignGuardian} reassignGuardian - the reassignGuardian transaction
 * @transaction
 */
function reassignGuardian(reassignGuardian) {
  var oldguardian = reassignGuardian.oldguardian;
  var newguardian = reassignGuardian.newguardian;
  var child = reassignGuardian.childform;
  child.guardian = newguardian;
  
  return getAssetRegistry('ibm.wsc.immunichain.Childform')
    .then(function(result) {
    	return result.update(child);
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

