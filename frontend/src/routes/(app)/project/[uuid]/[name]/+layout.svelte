<script lang="ts">
	import Help from '$lib/components/general/Help.svelte';
	import ProjectSidebar from '$lib/components/project/ProjectSidebar.svelte';
	import {
		columns,
		compareSort,
		comparisonColumn,
		comparisonModel,
		editTag,
		filterSelection,
		folders,
		metric,
		metricRange,
		metrics,
		model,
		models,
		project,
		rowsPerPage,
		selectionIds,
		selections,
		slices,
		tagIds,
		tags
	} from '$lib/stores.js';
	import { setURLParameters } from '$lib/util/util.js';

	export let data;

	// Only set stores and subscriptions if the project has changed.
	if ($project === undefined || $project.uuid !== data.project.uuid) {
		project.set(data.project);
		rowsPerPage.set(data.project.samplesPerPage ?? 10);
		slices.set(data.slices);
		columns.set(data.columns);
		models.set(data.models);
		metrics.set(data.metrics);
		folders.set(data.folders);
		tags.set(data.tags);
		model.set(data.model);
		metric.set(data.metric);
		comparisonModel.set(data.comparisonModel);
		comparisonColumn.set(data.comparisonColumn);
		compareSort.set(data.compareSort);
		metricRange.set(data.metricRange);
		selections.set(data.selections);
		selectionIds.set([]);
		filterSelection.set(false);
		editTag.set(undefined);
		// Set tagIds according to the selection we get from URL params
		tagIds.set(
			data.selections.tags.flatMap((selectionTag) => {
				const tag = data.tags.find((tag) => tag.id === selectionTag);
				if (tag === undefined) return [];
				return tag.dataIds;
			})
		);

		model.subscribe((mod) => {
			if ($comparisonModel && $comparisonModel === mod) {
				comparisonModel.set($models.filter((m) => m !== mod)[0]);
			}
		});
		// URL parameters set by metricRange subscription.
		metric.subscribe(() => metricRange.set([Infinity, -Infinity]));
		// URL parameters set by compareSort subscription.
		comparisonColumn.subscribe(() => compareSort.set([undefined, true]));
		comparisonModel.subscribe(() => setURLParameters());
		compareSort.subscribe(() => setURLParameters());
		metricRange.subscribe(() => setURLParameters());
		selections.subscribe(() => setURLParameters());
	}
</script>

<svelte:head>
	<title>{data.project.name} | Zeno</title>
	<meta name="description" content={data.project.description || 'Zeno Evaluation Project'} />
</svelte:head>

<div class="absolute bottom-14 right-3">
	<Help />
</div>

<ProjectSidebar user={data.user} />
<slot />
