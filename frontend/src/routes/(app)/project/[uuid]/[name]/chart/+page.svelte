<script lang="ts">
	import { goto } from '$app/navigation';
	import ChartHomeBlock from '$lib/components/chart/ChartHomeBlock.svelte';
	import { charts, project } from '$lib/stores';
	import { chartDefaults } from '$lib/util/charts';
	import { ChartType, ZenoService } from '$lib/zenoapi';
	import { mdiPlus } from '@mdi/js';
	import Button from '@smui/button/src/Button.svelte';
	import { Icon } from '@smui/icon-button';
	import { getContext } from 'svelte';

	export let data;

	const zenoClient = getContext('zenoClient') as ZenoService;

	$: charts.set(data.charts);
</script>

<div class="flex w-full flex-col p-8 pt-5">
	<div class="mb-1 flex h-12 items-center">
		<h3 class="mr-4 text-2xl">Charts</h3>
		{#if $project.editor}
			<Button
				on:click={() => {
					zenoClient
						.addChart($project.uuid, chartDefaults('New Chart', 0, $project.uuid, ChartType.BAR))
						.then((res) => {
							goto(
								`/project/${$project.uuid}/${encodeURIComponent(
									$project.name
								)}/chart/${res}?edit=true`
							);
						});
				}}
			>
				<Icon class="mr-2" width="24px" height="24px" tag="svg" viewBox="0 0 24 24">
					<path d={mdiPlus} />
				</Icon>
				New Chart
			</Button>
		{/if}
	</div>
	<div class="mb-6 h-0.5 w-full rounded-full bg-grey-light" />
	<div class="flex flex-wrap overflow-y-auto">
		{#each $charts.sort((a, b) => a.id - b.id) as chart}
			<ChartHomeBlock {chart} />
		{/each}
	</div>
</div>
