<script lang="ts">
	import { goto } from '$app/navigation';
	import { getContext } from 'svelte';
	const zenoClient = getContext('zenoClient') as ZenoService;
	import { chartDefaults } from '$lib/util/charts';

	import { mdiPlusCircle } from '@mdi/js';
	import { Icon } from '@smui/button';
	import ChartPopup from '../../popups/ChartPopup.svelte';
	import { selections } from '$lib/stores';
	import {
		Join,
		ZenoService,
		MetadataType,
		type FilterPredicate,
		type FilterPredicateGroup,
		type HistogramBucket,
		type ZenoColumn
	} from '$lib/zenoapi';
	import BinaryMetadataCell from './metadata-cells/BinaryMetadataCell.svelte';
	import ContinuousMetadataCell from './metadata-cells/ContinuousMetadataCell.svelte';
	import NominalMetadataCell from './metadata-cells/NominalMetadataCell.svelte';
	import TextMetadataCell from './metadata-cells/TextMetadataCell.svelte';

	export let col: ZenoColumn;
	export let histogram: HistogramBucket[];

	const columnMap = {
		[MetadataType.NOMINAL]: NominalMetadataCell,
		[MetadataType.CONTINUOUS]: ContinuousMetadataCell,
		[MetadataType.BOOLEAN]: BinaryMetadataCell,
		[MetadataType.DATETIME]: TextMetadataCell,
		[MetadataType.EMBEDDING]: TextMetadataCell,
		[MetadataType.OTHER]: TextMetadataCell
	};

	let filterPredicates: FilterPredicateGroup;
	$: filterPredicates = $selections.metadata[col.id]
		? $selections.metadata[col.id]
		: { predicates: [], join: Join._ };
	let predicates: FilterPredicate[] = [];
	$: predicates = filterPredicates.predicates as FilterPredicate[];

	function updatePredicates(predicates: FilterPredicate[]) {
		let metadata = {
			...$selections.metadata,
			[col.id]: { predicates, join: Join._ }
		};
		metadata = Object.keys(metadata)
			.filter((k) => metadata[k].predicates.length > 0)
			.reduce(
				(res, k) => ((res[k] = metadata[k]), res),
				{} as Record<string, FilterPredicateGroup>
			);
		selections.update((sel) => ({ ...sel, metadata: metadata }));
	}

	function getChartType(dataType: MetadataType, histogram: HistogramBucket[]) {
		if (dataType === MetadataType.NOMINAL && histogram.length == 0) {
			return columnMap[MetadataType.OTHER];
		} else {
			return columnMap[dataType];
		}
	}

	function createAllSlices() {
		// const predicates = predicateGroup.predicates[0];
		// if (Object.hasOwn(predicates, 'column'))
		// 	zenoClient
		// 		.addAllSlices(
		// 			$project.uuid,
		// 			(predicates as FilterPredicate).column,
		// 			sliceName === '' ? undefined : sliceName
		// 		)
		// 		.then(() => {
		// 			zenoClient
		// 				.getFolders($project.uuid)
		// 				.then((fetchedFolders) => folders.set(fetchedFolders));
		// 			zenoClient.getSlices($project.uuid).then((fetchedSlices) => slices.set(fetchedSlices));
		// 			dispatch('close');
		// 		})
		// 		.catch((err) => {
		// 			error = err.body['detail'];
		// 		});
	}

	function createChart() {
		// alert('createChart()');
		showNewChartPopup = true;
		// createAllSlices();
		// zenoClient
		// 	.addChart(
		// 		$project.uuid,
		// 		chartDefaults('New Chart', 0, $project.uuid, ChartType.BAR)
		// 	)
		// 	.then((res) => {
		// 		goto(
		// 			`/project/${$project.uuid}/${encodeURIComponent(
		// 				$project.name
		// 			)}/chart/${res}?edit=true`
		// 		);
		// 	});
	}

	let showNewChartPopup = false;
</script>

{#if showNewChartPopup}
	<ChartPopup on:close={() => (showNewChartPopup = false)} />
{/if}

{#if histogram}
	<div class="group flex flex-col border-b border-grey-lighter pb-2 pt-2">
		<div class="mb-2.5 ml-1 flex items-start justify-between text-grey-darker">
			<div class="label top-text">
				<span>
					{col.name}
				</span>
			</div>
			{#if col.dataType === MetadataType.NOMINAL && histogram.length > 0}
				<button
					class="h-0 items-center justify-center transition hidden group-hover:flex"
					on:click={() => createChart()}
				>
					<div class="h-0 items-center justify-center bg-primary-dark mr-4">
							<Icon style="outline:none; width: 24px; height: 24px" tag="svg" viewBox="0 0 24 24">
								<path class="fill-primary-dark" d={mdiPlusCircle} />
							</Icon>
					</div>
				</button>
			{/if}
		</div>
		<svelte:component
			this={getChartType(col.dataType, histogram)}
			filterPredicates={predicates}
			{updatePredicates}
			{col}
			{histogram}
		/>
	</div>
{/if}
