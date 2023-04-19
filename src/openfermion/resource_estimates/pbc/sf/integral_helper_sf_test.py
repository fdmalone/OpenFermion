# coverage: ignore
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import numpy as np
from pyscf.pbc import mp, cc
import pytest
from openfermion.resource_estimates.pbc.utils.cc_helper import build_approximate_eris

from openfermion.resource_estimates.pbc.sf.integral_helper_sf import (
    SingleFactorizationHelper,
)
from openfermion.resource_estimates.pbc.utils.hamiltonian_utils import (
    cholesky_from_df_ints,
)
from openfermion.resource_estimates.pbc.utils.test_utils import make_diamond_113_szv


def test_sf_helper_trunc():
    mf = make_diamond_113_szv()
    exact_cc = cc.KRCCSD(mf)
    eris = exact_cc.ao2mo()
    exact_emp2, _, _ = exact_cc.init_amps(eris)

    mymp = mp.KMP2(mf)

    Luv = cholesky_from_df_ints(mymp)  # [kpt, kpt, naux, nao, nao]
    naux = Luv[0, 0].shape[0]

    print(" naux  error (Eh)")
    approx_cc = cc.KRCCSD(mf)
    approx_cc.verbose = 4
    helper = SingleFactorizationHelper(cholesky_factor=Luv, kmf=mf, naux=10)

    eris = build_approximate_eris(approx_cc, helper)
    emp2, _, _ = approx_cc.init_amps(eris)
    assert not np.isclose(emp2, exact_emp2)

    out_eris = build_approximate_eris(approx_cc, helper)
    emp2_2, _, _ = approx_cc.init_amps(out_eris)
    assert not np.isclose(emp2, exact_emp2)
    assert np.isclose(emp2, emp2_2)
    helper = SingleFactorizationHelper(cholesky_factor=Luv, kmf=mf, naux=5)
    out_eris = build_approximate_eris(approx_cc, helper)
    emp2_2, _, _ = approx_cc.init_amps(out_eris)
    assert not np.isclose(emp2, exact_emp2)
    assert not np.isclose(emp2, emp2_2)
    out_eris = build_approximate_eris(approx_cc, helper, eris=eris)
    emp2_3, _, _ = approx_cc.init_amps(out_eris)
    assert not np.isclose(emp2, exact_emp2)
    assert np.isclose(emp2_2, emp2_3)

    helper = SingleFactorizationHelper(cholesky_factor=Luv, kmf=mf, naux=naux)
    out_eris = build_approximate_eris(approx_cc, helper)
    emp2, _, _ = approx_cc.init_amps(out_eris)
    assert np.isclose(emp2, exact_emp2)
