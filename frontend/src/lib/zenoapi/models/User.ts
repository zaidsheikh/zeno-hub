/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Representation of a user in Zeno.
 *
 * Attributes:
 * id (int): ID of the user.
 * name (str): name of the user.
 * cognito_id (str | None): Cognito ID of the user. Default None.
 * admin (bool | None): whether the user is an admin. Default None.
 */
export type User = {
	id: number;
	name: string;
	cognitoId?: string | null;
	admin?: boolean | null;
};
