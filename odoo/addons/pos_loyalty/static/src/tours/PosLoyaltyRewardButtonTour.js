/** @odoo-module **/

import { PosLoyalty } from 'pos_loyalty.tour.PosCouponTourMethods';
import { ProductScreen } from 'point_of_sale.tour.ProductScreenTourMethods';
import { SelectionPopup } from 'point_of_sale.tour.SelectionPopupTourMethods';
import { getSteps, startSteps } from 'point_of_sale.tour.utils';
import Tour from 'web_tour.tour';

startSteps();

ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.exec.addOrderline('Desk Organizer', '2');

// At this point, the free_product program is triggered.
// The reward button should be highlighted.
PosLoyalty.check.isRewardButtonHighlighted(true);
// Since the reward button is highlighted, clicking the reward product should be added as reward.
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '3.00');
PosLoyalty.check.hasRewardLine('Free Product - Desk Organizer', '-5.10', '1.00');
// In the succeeding 2 clicks on the product, it is considered as a regular product.
// In the third click, the product will be added as reward.
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
PosLoyalty.check.isRewardButtonHighlighted(true);
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '6.00');
PosLoyalty.check.hasRewardLine('Free Product - Desk Organizer', '-10.20', '2.00');


ProductScreen.do.clickDisplayedProduct('Desk Organizer');
PosLoyalty.check.isRewardButtonHighlighted(false);
PosLoyalty.check.orderTotalIs('25.50');
// Finalize order that consumed a reward.
PosLoyalty.exec.finalizeOrder('Cash');

ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '1.00');
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '2.00');
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
PosLoyalty.check.hasRewardLine('Free Product - Desk Organizer', '-5.10', '1.00');
ProductScreen.do.pressNumpad('Backspace');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '0.00');
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '1.00');
ProductScreen.do.clickDisplayedProduct('Desk Organizer');
ProductScreen.check.selectedOrderlineHas('Desk Organizer', '2.00');
PosLoyalty.check.isRewardButtonHighlighted(true);
// Finalize order but without the reward.
// This step is important. When syncing the order, no reward should be synced.
PosLoyalty.check.orderTotalIs('10.20');
PosLoyalty.exec.finalizeOrder('Cash');


ProductScreen.exec.addOrderline('Magnetic Board', '2');
PosLoyalty.check.isRewardButtonHighlighted(false);
ProductScreen.do.clickDisplayedProduct('Magnetic Board');
PosLoyalty.check.isRewardButtonHighlighted(true);
ProductScreen.do.clickDisplayedProduct('Whiteboard Pen');
PosLoyalty.check.isRewardButtonHighlighted(false);
PosLoyalty.check.hasRewardLine('Free Product - Whiteboard Pen', '-3.20', '1.00');
ProductScreen.do.clickOrderline('Magnetic Board', '3.00');
ProductScreen.check.selectedOrderlineHas('Magnetic Board', '3.00');
ProductScreen.do.pressNumpad('6');
ProductScreen.check.selectedOrderlineHas('Magnetic Board', '6.00');
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
PosLoyalty.check.isRewardButtonHighlighted(false);
PosLoyalty.check.hasRewardLine('Free Product - Whiteboard Pen', '-6.40', '2.00');
// Finalize order that consumed a reward.
PosLoyalty.check.orderTotalIs('11.88');
PosLoyalty.exec.finalizeOrder('Cash');

ProductScreen.exec.addOrderline('Magnetic Board', '6');
ProductScreen.do.clickDisplayedProduct('Whiteboard Pen');
PosLoyalty.check.hasRewardLine('Free Product - Whiteboard Pen', '-3.20', '1.00');
PosLoyalty.check.isRewardButtonHighlighted(true);

ProductScreen.do.clickOrderline('Magnetic Board', '6.00');
ProductScreen.do.pressNumpad('Backspace');
// At this point, the reward should have been removed.
PosLoyalty.check.isRewardButtonHighlighted(false);
ProductScreen.check.selectedOrderlineHas('Magnetic Board', '0.00');
ProductScreen.do.clickDisplayedProduct('Magnetic Board');
ProductScreen.check.selectedOrderlineHas('Magnetic Board', '1.00');
ProductScreen.do.clickDisplayedProduct('Magnetic Board');
ProductScreen.check.selectedOrderlineHas('Magnetic Board', '2.00');
ProductScreen.do.clickDisplayedProduct('Magnetic Board');
ProductScreen.check.selectedOrderlineHas('Magnetic Board', '3.00');
PosLoyalty.check.hasRewardLine('Free Product - Whiteboard Pen', '-3.20', '1.00');
PosLoyalty.check.isRewardButtonHighlighted(false);

PosLoyalty.check.orderTotalIs('5.94');
PosLoyalty.exec.finalizeOrder('Cash');

// Promotion: 2 items of shelves, get desk_pad/monitor_stand free
// This is the 5th order.
ProductScreen.do.clickDisplayedProduct('Wall Shelf Unit');
ProductScreen.check.selectedOrderlineHas('Wall Shelf Unit', '1.00');
PosLoyalty.check.isRewardButtonHighlighted(false);
ProductScreen.do.clickDisplayedProduct('Small Shelf');
ProductScreen.check.selectedOrderlineHas('Small Shelf', '1.00');
PosLoyalty.check.isRewardButtonHighlighted(true);
// Click reward product. Should be automatically added as reward.
ProductScreen.do.clickDisplayedProduct('Desk Pad');
PosLoyalty.check.isRewardButtonHighlighted(false);
PosLoyalty.check.hasRewardLine('Free Product', '-1.98', '1.00');
// Remove the reward line. The next steps will check if cashier
// can select from the different reward products.
ProductScreen.do.pressNumpad('Backspace');
ProductScreen.do.pressNumpad('Backspace');
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
SelectionPopup.check.hasSelectionItem('Monitor Stand');
SelectionPopup.check.hasSelectionItem('Desk Pad');
SelectionPopup.do.clickItem('Desk Pad');
PosLoyalty.check.isRewardButtonHighlighted(false);
PosLoyalty.check.hasRewardLine('Free Product', '-1.98', '1.00');
ProductScreen.do.pressNumpad('Backspace');
ProductScreen.do.pressNumpad('Backspace');
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.claimReward('Monitor Stand');
PosLoyalty.check.isRewardButtonHighlighted(false);
ProductScreen.check.selectedOrderlineHas('Monitor Stand', '1.00', '3.19');
PosLoyalty.check.hasRewardLine('Free Product', '-3.19', '1.00');
PosLoyalty.check.orderTotalIs('4.81');
PosLoyalty.exec.finalizeOrder('Cash');

Tour.register('PosLoyaltyFreeProductTour', { test: true, url: '/pos/web' }, getSteps());

startSteps();

ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.do.clickPartnerButton();
ProductScreen.do.clickCustomer('AAA Partner');
ProductScreen.exec.addOrderline('Test Product A', '1');
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
PosLoyalty.check.hasRewardLine('Free Product - Test Product A', '-11.50', '1.00');

Tour.register('PosLoyaltyFreeProductTour2', { test: true, url: '/pos/web' }, getSteps());

startSteps();

ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.do.clickDisplayedProduct('Test Product A');
ProductScreen.check.selectedOrderlineHas('Test Product A', '1.00', '40.00');
ProductScreen.do.clickDisplayedProduct('Test Product B');
ProductScreen.check.selectedOrderlineHas('Test Product B', '1.00', '40.00');
PosLoyalty.do.clickRewardButton();
SelectionPopup.do.clickItem("$ 10 per order on specific products");
PosLoyalty.check.hasRewardLine('$ 10 per order on specific products', '-10.00', '1.00');
PosLoyalty.check.orderTotalIs('70.00');
PosLoyalty.do.clickRewardButton();
SelectionPopup.do.clickItem("$ 10 per order on specific products");
PosLoyalty.check.orderTotalIs('60.00');
PosLoyalty.do.clickRewardButton();
SelectionPopup.do.clickItem("$ 30 per order on specific products");
PosLoyalty.check.hasRewardLine('$ 30 per order on specific products', '-30.00', '1.00');
PosLoyalty.check.orderTotalIs('30.00');

Tour.register('PosLoyaltySpecificDiscountTour', { test: true, url: '/pos/web' }, getSteps());

startSteps();

ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.do.clickDisplayedProduct('Test Product A');
ProductScreen.do.clickDisplayedProduct('Test Product C');
PosLoyalty.check.orderTotalIs('130.00');
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
PosLoyalty.check.orderTotalIs('130.00');

Tour.register('PosLoyaltySpecificDiscountWithFreeProductTour', { test: true, url: '/pos/web' }, getSteps());

startSteps();

ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.do.clickDisplayedProduct('Product A');
ProductScreen.check.selectedOrderlineHas('Product A', '1.00', '15.00');
PosLoyalty.check.orderTotalIs('15.00');

ProductScreen.do.clickDisplayedProduct('Product B');
ProductScreen.check.selectedOrderlineHas('Product B', '1.00', '50.00');
PosLoyalty.check.orderTotalIs('40.00');

Tour.register('PosLoyaltySpecificDiscountWithRewardProductDomainTour', { test: true, url: '/pos/web' }, getSteps());

startSteps();

ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.do.clickDisplayedProduct('Product A');
ProductScreen.check.selectedOrderlineHas('Product A', '1.00', '15.00');
PosLoyalty.check.orderTotalIs('15.00');

ProductScreen.do.clickDisplayedProduct('Product B');
ProductScreen.check.selectedOrderlineHas('Product B', '1.00', '50.00');
PosLoyalty.check.orderTotalIs('40.00');

Tour.register('PosLoyaltySpecificDiscountCategoryTour', { test: true, url: '/pos/web' }, getSteps());

startSteps();
ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();

ProductScreen.do.clickDisplayedProduct("Desk Organizer");
ProductScreen.do.clickDisplayedProduct("Desk Organizer");
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
SelectionPopup.do.clickItem("product_a");
PosLoyalty.check.hasRewardLine("Free Product", "-2", "1.00");
PosLoyalty.check.isRewardButtonHighlighted(false);

ProductScreen.do.clickDisplayedProduct("Desk Organizer");
ProductScreen.do.clickDisplayedProduct("Desk Organizer");
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
SelectionPopup.do.clickItem("product_b");
PosLoyalty.check.hasRewardLine("Free Product", "-5", "1.00");
PosLoyalty.check.isRewardButtonHighlighted(false);

ProductScreen.do.clickDisplayedProduct("Desk Organizer");
ProductScreen.do.clickDisplayedProduct("Desk Organizer");
PosLoyalty.check.isRewardButtonHighlighted(true);
PosLoyalty.do.clickRewardButton();
SelectionPopup.do.clickItem("product_b");
PosLoyalty.check.hasRewardLine("Free Product", "-10", "2.00");
PosLoyalty.check.isRewardButtonHighlighted(false);

Tour.register("PosLoyaltyRewardProductTag", { test: true, url: "/pos/web" }, getSteps());

startSteps();
ProductScreen.do.confirmOpeningPopup();
ProductScreen.do.clickHomeCategory();
ProductScreen.do.clickDisplayedProduct('Product A');
PosLoyalty.do.enterCode('563412');
PosLoyalty.check.hasRewardLine('10% on your order', '-1.50');

Tour.register("test_loyalty_on_order_with_fixed_tax", { test: true, url: "/pos/web" }, getSteps());
