# -*- coding: utf-8 -*-

import itertools

import pytest

import amrex

if amrex.Config.have_mpi:
    from mpi4py import MPI


@pytest.fixture(autouse=True, scope="function")
def amrex_init():
    amrex.initialize(
        [
            # print AMReX status messages
            "amrex.verbose=2",
            # throw exceptions and create core dumps instead of
            # AMReX backtrace files: allows to attach to
            # debuggers
            "amrex.throw_exception=1",
            "amrex.signal_handling=0",
            # abort GPU runs if out-of-memory instead of swapping to host RAM
            # "abort_on_out_of_gpu_memory=1",
        ]
    )
    yield
    amrex.finalize()


@pytest.fixture(scope="function")
def std_real_box():
    """Standard RealBox for common problem domains"""
    rb = amrex.RealBox(0, 0, 0, 1.0, 1.0, 1.0)
    return rb


@pytest.fixture(scope="function")
def std_box():
    """Standard Box for tests"""
    bx = amrex.Box(amrex.IntVect(0, 0, 0), amrex.IntVect(63, 63, 63))
    return bx


@pytest.fixture(scope="function")
def std_geometry(std_box, std_real_box):
    """Standard Geometry"""
    coord = 1  # RZ
    periodicity = [0, 0, 1]
    gm = amrex.Geometry(std_box, std_real_box, coord, periodicity)
    return gm


@pytest.fixture(scope="function")
def boxarr(std_box):
    """BoxArray for MultiFab creation"""
    ba = amrex.BoxArray(std_box)
    ba.max_size(32)
    return ba


@pytest.fixture(scope="function")
def distmap(boxarr):
    """DistributionMapping for MultiFab creation"""
    dm = amrex.DistributionMapping(boxarr)
    return dm


@pytest.fixture(scope="function", params=list(itertools.product([1, 3], [0, 1])))
def make_mfab(boxarr, distmap, request):
    """MultiFab that is either managed or device:
    The MultiFab object itself is not a fixture because we want to avoid caching
    it between amrex.initialize/finalize calls of various tests.
    https://github.com/pytest-dev/pytest/discussions/10387
    https://github.com/pytest-dev/pytest/issues/5642#issuecomment-1279612764
    """

    def create():
        num_components = request.param[0]
        num_ghost = request.param[1]
        mfab = amrex.MultiFab(boxarr, distmap, num_components, num_ghost)
        mfab.set_val(0.0, 0, num_components)
        return mfab

    return create


@pytest.mark.skipif(
    amrex.Config.gpu_backend != "CUDA", reason="Requires AMReX_GPU_BACKEND=CUDA"
)
@pytest.fixture(scope="function", params=list(itertools.product([1, 3], [0, 1])))
def make_mfab_device(boxarr, distmap, request):
    """MultiFab that resides purely on the device:
    The MultiFab object itself is not a fixture because we want to avoid caching
    it between amrex.initialize/finalize calls of various tests.
    https://github.com/pytest-dev/pytest/discussions/10387
    https://github.com/pytest-dev/pytest/issues/5642#issuecomment-1279612764
    """

    def create():
        num_components = request.param[0]
        num_ghost = request.param[1]
        mfab = amrex.MultiFab(
            boxarr,
            distmap,
            num_components,
            num_ghost,
            amrex.MFInfo().set_arena(amrex.The_Device_Arena()),
        )
        mfab.set_val(0.0, 0, num_components)
        return mfab

    return create
