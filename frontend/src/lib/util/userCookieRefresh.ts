import { dev } from '$app/environment';
import { env as private_env } from '$env/dynamic/private';
import { extractUserFromSession, refreshAccessToken } from '$lib/auth/cognito.js';
import type { AuthUser } from '$lib/auth/types';
import type { Cookies } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

export async function getOrRefreshCognitoUser(
	cookies: Cookies,
	url: URL
): Promise<AuthUser | null> {
	const loggedInCookie = cookies.get('loggedIn');
	if (loggedInCookie === undefined) {
		return null;
	}

	let cognitoUser = JSON.parse(loggedInCookie);
	if (new Date() > new Date(cognitoUser.accessTokenExpires * 1000)) {
		try {
			const res = await refreshAccessToken(cognitoUser.refreshToken);
			cognitoUser = extractUserFromSession(res);
			cookies.set('loggedIn', JSON.stringify(cognitoUser), {
				path: '/',
				httpOnly: true,
				sameSite: 'strict',
				secure: !dev && private_env.ALLOW_INSECURE_HTTP != 'true',
				maxAge: 60 * 60 * 24 * 30
			});
		} catch (error) {
			throw redirect(303, `/login?redirectTo=${url.pathname}`);
		}
	}

	return cognitoUser;
}
