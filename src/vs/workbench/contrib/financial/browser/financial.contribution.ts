/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { Registry } from '../../../../platform/registry/common/platform.js';
import { IWorkbenchContributionsRegistry, Extensions as WorkbenchExtensions, IWorkbenchContribution } from '../../../common/contributions.js';
import { LifecyclePhase } from '../../../services/lifecycle/common/lifecycle.js';
import { Extensions as ViewExtensions, IViewsRegistry, IViewDescriptor, IViewContainersRegistry, ViewContainerLocation } from '../../../common/views.js';
import { Generic2by2 } from '../../../../base/common/codicons.js';
import { SyncDescriptor } from '../../../../platform/instantiation/common/descriptors.js';
import { ViewPaneContainer } from '../../../browser/parts/views/viewPaneContainer.js';
import { FinancialView } from './financialView.js';
import { localize } from '../../../../nls.js';

// Register View Container (Sidebar Icon)
const VIEW_CONTAINER = Registry.as<IViewContainersRegistry>(ViewExtensions.ViewContainersRegistry).registerViewContainer({
    id: 'investigative.financial',
    title: localize('financial', "Financial Tools"),
    ctorDescriptor: new SyncDescriptor(ViewPaneContainer, ['investigative.financial', { mergeViewWithContainerWhenSingleView: true }]),
    icon: Generic2by2, // Placeholder icon
    order: 0,
    storageId: 'investigative.financial'
}, ViewContainerLocation.Sidebar);

// Register View
const viewsRegistry = Registry.as<IViewsRegistry>(ViewExtensions.ViewsRegistry);
viewsRegistry.registerViews([{
    id: 'investigative.financial.view',
    name: localize('financialView', "Forensic Actions"),
    containerIcon: Generic2by2,
    ctorDescriptor: new SyncDescriptor(FinancialView),
    canToggleVisibility: true,
    workspace: true,
    canMoveView: true
}], VIEW_CONTAINER);

class FinancialContribution implements IWorkbenchContribution {
    constructor() {
        console.log('InvestigativeOS Financial Suite Loaded');
    }
}

Registry.as<IWorkbenchContributionsRegistry>(WorkbenchExtensions.Workbench).registerWorkbenchContribution(FinancialContribution, LifecyclePhase.Restored);
