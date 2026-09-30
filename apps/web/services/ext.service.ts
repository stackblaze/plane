/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import { APIService } from "@/services/api.service";

export class ExtService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async list(path: string) {
    return this.get(`/api/${path}`).then((response) => response?.data);
  }

  async create(path: string, data: Record<string, unknown>) {
    return this.post(`/api/${path}`, data).then((response) => response?.data);
  }

  async update(path: string, data: Record<string, unknown>) {
    return this.patch(`/api/${path}`, data).then((response) => response?.data);
  }

  async remove(path: string) {
    return this.delete(`/api/${path}`).then((response) => response?.data);
  }
}

export const extService = new ExtService();
