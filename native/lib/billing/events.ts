/**
 * Subscription ID referenced by a webhook event object.
 * API 2025-03-31+ moved an invoice's subscription to invoice.parent.subscription_details.subscription.
 */
export function subscriptionIdFromEvent(type:string,o:Record<string,unknown>):string|null{
 if(type.startsWith("customer.subscription."))return typeof o.id==="string"?o.id:null;
 if(typeof o.subscription==="string")return o.subscription;
 const parent=o.parent as {subscription_details?:{subscription?:unknown}}|undefined;
 const nested=parent?.subscription_details?.subscription;
 return typeof nested==="string"?nested:null;
}
