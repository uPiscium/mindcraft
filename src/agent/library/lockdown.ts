import 'ses';

// This sets up the secure environment
// We disable some of the taming to allow for more flexibility
//

let lockeddown: boolean = false;
export function initLockdown(): void {
  if (lockeddown) return;
  lockeddown = true;
  lockdown({
    // basic devex and quality of life improvements
    localeTaming: 'unsafe',
    consoleTaming: 'unsafe',
    errorTaming: 'unsafe',
    stackFiltering: 'verbose',
    // allow eval outside of created compartments
    // (mineflayer dep "protodef" uses eval)
    evalTaming: 'unsafeEval',
  });
}

export const makeCompartment = (endowments = {}) => {
  return new Compartment({
    // provide untamed Math, Date, etc
    Math,
    Date,
    // standard endowments
    ...endowments
  });
};
