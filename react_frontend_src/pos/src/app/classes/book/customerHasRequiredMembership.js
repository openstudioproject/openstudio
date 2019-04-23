export default function customerHasRequiredMembership(required_membership_id, customer_memberships) {
    if (!customer_memberships.length) {
        return false
    } else {
        let i
        let m
        let found = false
        for (i = 0; i < customer_memberships.length; i++) { 
            m = customer_memberships[i]
            if (m.school_memberships_id == required_membership_id) {
                found = true
                break
            }
        }
        return found
    }
}
