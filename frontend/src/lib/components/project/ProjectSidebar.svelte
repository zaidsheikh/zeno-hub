<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import ProjectPopup from '$lib/components/popups/ProjectPopup.svelte';
	import { collapseHeader, models, project } from '$lib/stores';
	import { getProjectRouteFromURL } from '$lib/util/util';
	import type { User } from '$lib/zenoapi';
	import {
		mdiArrowCollapseLeft,
		mdiArrowCollapseRight,
		mdiChartBoxOutline,
		mdiCogOutline,
		mdiCompare,
		mdiCompassOutline
	} from '@mdi/js';
	import HeaderIcon from '../general/HeaderIcon.svelte';

	export let user: User | null;

	let projectEdit = false;

	$: currentTab = $page.url.href.split('/').pop();
</script>

{#if projectEdit && user !== null}
	<ProjectPopup config={$project} on:close={() => (projectEdit = false)} {user} />
{/if}
<nav class="z-20 flex md:hidden">
	<header
		class="flex w-full flex-col items-center justify-between border-r border-x-grey-lighter bg-yellowish text-grey"
	>
		<a href="/">
			<img class="w-8 pb-2 pt-2" src="/zeno.png" alt="Square spiral logo next to 'Zeno'" />
		</a>
	</header>
</nav>
<nav class="z-20 hidden md:flex">
	<header
		class="flex h-full w-12 flex-col items-center justify-between border-r border-x-grey-lighter bg-yellowish text-grey"
	>
		<div class="flex flex-col items-center justify-center">
			<a href="/">
				<img class="mt-5 w-8" src="/zeno.png" alt="Square spiral logo next to 'Zeno'" />
			</a>
			{#if $page.url.href.includes('project/')}
				<div class="mt-3 flex flex-col">
					<HeaderIcon
						pageName={'explore'}
						tooltipContent={'Explore your data and system outputs'}
						icon={mdiCompassOutline}
						on:click={() => goto(getProjectRouteFromURL($page.url))}
					/>
					{#if $models.length > 1 && $project.view !== ''}
						<HeaderIcon
							pageName={'compare'}
							tooltipContent={'Qualitatively compare system outputs'}
							icon={mdiCompare}
							on:click={() => goto(`${getProjectRouteFromURL($page.url)}/compare`)}
						/>
					{/if}
					<HeaderIcon
						pageName={'chart'}
						tooltipContent={'Create charts from your slices and metrics'}
						icon={mdiChartBoxOutline}
						on:click={() => goto(`${getProjectRouteFromURL($page.url)}/chart`)}
					/>
				</div>
			{/if}
		</div>
		<div>
			{#if currentTab?.includes('explore') || currentTab?.includes('compare')}
				<HeaderIcon
					pageName={'$collapseHeader'}
					tooltipContent={$collapseHeader ? 'Expand sidebar' : 'Collapse sidebar'}
					icon={$collapseHeader ? mdiArrowCollapseRight : mdiArrowCollapseLeft}
					on:click={() => collapseHeader.set(!$collapseHeader)}
				/>
			{/if}
		</div>
		<div class="mb-3 flex flex-col items-center justify-center">
			{#if $page.url.pathname.startsWith('/project/') && $project?.ownerName === user?.name}
				<HeaderIcon
					pageName={'editProject'}
					tooltipContent={"Edit your project's configuration"}
					icon={mdiCogOutline}
					on:click={() => (projectEdit = true)}
				/>
			{/if}
		</div>
	</header>
</nav>
