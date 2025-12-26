/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { Registry } from '../../../../platform/registry/common/platform.js';
import { IWorkbenchContributionsRegistry, Extensions as WorkbenchExtensions, IWorkbenchContribution } from '../../../common/contributions.js';
import { LifecyclePhase } from '../../../services/lifecycle/common/lifecycle.js';
import { Extensions as ViewExtensions, IViewsRegistry, IViewContainer, ViewContainerLocation } from '../../../common/views.js';
import { SyncDescriptor } from '../../../../platform/instantiation/common/descriptors.js';
import { AIView } from './aiView.js';
import { localize } from '../../../../nls.js';
import { Generic2by2 } from '../../../../base/common/codicons.js';

// Register View into the SAME container as Financial Tools, or a new one?
// Let's put it in the same "Investigative Tools" container if possible, or new one.
// We'll use the ID we defined in financial.contribution.ts: 'investigative.financial'
// Note: To share the container, we need to ensure the container is registered only once.
// For safety/simplicity in this overlay, we will add it to the same container ID.

const viewsRegistry = Registry.as<IViewsRegistry>(ViewExtensions.ViewsRegistry);
viewsRegistry.registerViews([{
    id: 'investigative.ai.view',
    name: localize('aiView', "Local AI (4B)"),
    containerIcon: Generic2by2,
    ctorDescriptor: new SyncDescriptor(AIView),
    canToggleVisibility: true,
    workspace: true,
    canMoveView: true
}], { id: 'investigative.financial', title: 'Financial Tools', ctorDescriptor: null! }); 

class AIContribution implements IWorkbenchContribution {
    constructor() {
        console.log('AI Module Contribution Loaded');
    }
}

Registry.as<IWorkbenchContributionsRegistry>(WorkbenchExtensions.Workbench).registerWorkbenchContribution(AIContribution, LifecyclePhase.Restored);
